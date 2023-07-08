package http

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/internal/domain"
	"github.com/scribe-security/scribe2/scribe-service/internal/transport"
	"github.com/scribe-security/scribe2/scribe-service/pkg/config"
	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
	"github.com/scribe-security/scribe2/scribe-service/pkg/middlewares/auth"
)

// EVSTHandler serves all requests for upload and manage files to a cloud storages
type EVSTHandler struct {
	s domain.EvidenceStoreService
}

// NewEVSTHandler instance constructor
func NewEVSTHandler(
	r fiber.Router,
	s domain.EvidenceStoreService,
	auth0Cfg *config.Auth0,
) *EVSTHandler {
	handler := &EVSTHandler{
		s: s,
	}

	r.Use(auth.New(auth0Cfg.Domain))
	r.Post("/", handler.uploadEvidence)
	r.Post("/finish", handler.finishUploadEvidence)
	r.Post("/list", handler.listEvidenceByContext)
	r.Get("/:file_id", handler.downloadEvidence)
	r.Delete("/:file_id", handler.delete)
	return handler
}

// uploadEvidence returns the presignedURL for a new evidence context
//
// swagger:route POST /evidence evidence uploadEvidenceAction
//
// Create presigned URL to POST file content.
//
// This endpoint is used to upload evidence to the cloud storage.
// It returns a presigned URL to upload the file content.
// After uploading the file content, the client should call `/evidence/finish`.
//
//	Consumes:
//	- application/json
//
//	Produces:
//	- application/json
//
//	Schemes: https
//
//	Security:
//	  JWT:
//
//	Responses:
//	  200: createEvidenceOutput
//	  403: errorResponse
//	  400: errorResponse
func (h *EVSTHandler) uploadEvidence(c *fiber.Ctx) error {
	ctx := c.UserContext()
	c.Accepts("application/json")

	var in domain.UploadEvidenceInput
	if err := c.BodyParser(&in.Body); err != nil {
		log.L(ctx).Error("parse body of the request", zap.Error(err))
		return err
	}

	_, teamID, err := h.getTokenAndTeamID(ctx, c)
	if err != nil {
		return err
	}

	out, err := h.s.CreateEvidence(ctx, &domain.UploadEvidenceFileTransfer{
		Key:         in.Body.Key,
		TeamID:      teamID,
		ContentType: in.Body.ContentType,
		ContextType: in.Body.ContextType,
		ContextData: in.Body.ContextData,
	})
	switch err {
	case nil:
		return c.JSON(out)
	case domain.ErrInvalidProductKey:
		log.L(ctx).Error("invalid product key", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusBadRequest,
			Message:    "add product key flag or run agent from a git repository directory",
		}
		return herr.WriteToResponse(c)
	case domain.ErrInvalidPipelineParams:
		log.L(ctx).Error("invalid pipeline params", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusBadRequest,
			Message:    "invalid input flags",
		}
		return herr.WriteToResponse(c)
	default:
		log.L(ctx).Error("internal error", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusInternalServerError,
			Message:    "internal error",
		}
		return herr.WriteToResponse(c)
	}
}

// finish action to invoke FinishEvidenceUpload service call
//
// swagger:route POST /evidence/finish evidence finishUploadEvidenceAction
//
// Mark file transfer as finished.
//
// Push file transfer result after POST file content.
//
//	Consumes:
//	- application/json
//
//	Produces:
//	- application/json
//
//	Schemes: https
//
//	Security:
//	  JWT:
//
//	Responses:
//	  200:
//	  400: errorResponse
//	  403: errorResponse
//	  500: errorResponse
func (h *EVSTHandler) finishUploadEvidence(c *fiber.Ctx) error {
	ctx := c.UserContext()
	c.Accepts("application/json")

	var in domain.FinishUploadEvidenceInput
	if err := c.BodyParser(&in.Body); err != nil {
		log.L(ctx).Error("parse body of the request", zap.Error(err))
		return err
	}

	tokenStr, teamID, err := h.getTokenAndTeamID(ctx, c)
	if err != nil {
		return err
	}

	if err := h.s.FinishEvidenceFileTransfer(ctx, &domain.FinishUploadEvidenceWithTeamID{
		FileID: in.Body.FileID,
		Error:  in.Body.Error,
		TeamID: teamID,
	}); err != nil {
		log.L(ctx).Error("unable to finish upload", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusBadRequest, Message: "unable set finish status",
		}
		return herr.WriteToResponse(c)
	}

	properties := []domain.MixapanelProperties{
		{
			Key:   "File ID",
			Value: fmt.Sprint(in.Body.FileID),
		},
		{
			Key:   "Team ID",
			Value: fmt.Sprint(teamID),
		},
	}

	if err := h.s.SendMixpanelEvent(ctx, &domain.SendMixpanelEventInputs{
		EventName:  "BE: User uploaded SBOM",
		Properties: properties,
		UserToken:  tokenStr,
		TokenType:  domain.MixpanelTokenGensbom,
		IP:         c.IP(),
	}); err != nil {
		log.L(ctx).Error("unable to send event to mixpanel", zap.Error(err))
	}

	return nil
}

// downloadEvidence returns the presignedURL for a download evidence
//
// swagger:route GET /evidence/{file_id} evidence downloadEvidenceAction
//
// Create presigned URL to POST file content.
//
// This endpoint is used to upload evidence to the cloud storage.
// It returns a presigned URL to upload the file content.
// After uploading the file content, the client should call `/evidence/finish`.
//
//	Consumes:
//	- application/json
//
//	Produces:
//	- application/json
//
//	Schemes: https
//
//	Security:
//	  JWT:
//
//	Responses:
//	  200: getEvidenceDownloadOutput
//	  403: errorResponse
//	  400: errorResponse
func (h *EVSTHandler) downloadEvidence(c *fiber.Ctx) error {
	ctx := c.UserContext()
	c.Accepts("application/json")

	fileID, err := strconv.Atoi(c.Params("file_id"))
	if err != nil {
		log.L(ctx).Error("unable to convert file_id to number", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusBadRequest,
			Message:    "unable to convert file_id to number",
		}
		return herr.WriteToResponse(c)
	}

	tokenStr, teamID, err := h.getTokenAndTeamID(ctx, c)
	if err != nil {
		return err
	}

	out, err := h.s.GetEvidenceDownload(ctx, &domain.GetEvidenceDownloadInput{
		FileID: fileID,
		TeamID: teamID,
	})

	if err == domain.ErrFileTransferAccessDenied {
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusBadRequest,
			Message:    "unable to get presigned URL: access denied",
		}
		return herr.WriteToResponse(c)
	}
	if err != nil {
		log.L(ctx).Error("unable to get presigned URL", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusBadRequest,
			Message:    "unable to get presigned URL",
		}
		return herr.WriteToResponse(c)
	}

	properties := []domain.MixapanelProperties{
		{
			Key:   "File ID",
			Value: fmt.Sprint(fileID),
		},
		{
			Key:   "Team ID",
			Value: fmt.Sprint(teamID),
		},
	}

	err = h.s.SendMixpanelEvent(ctx, &domain.SendMixpanelEventInputs{
		EventName:  "BE: downloaded SBOM",
		Properties: properties,
		UserToken:  tokenStr,
		TokenType:  domain.MixpanelTokenFrontend,
		IP:         c.IP(),
	})
	if err != nil {
		log.L(ctx).Error("unable to send event to mixpanel", zap.Error(err))
	}

	return c.JSON(out)
}

// delete file by file_id or list files by key pattern
//
// swagger:route DELETE /evidence/{file_id} evidence deleteEvidenceAction
//
// Delete evidence object.
//
// <p>Delete evidence object by <b>file_id</b>.
//
//	Consumes:
//	- application/json
//
//	Produces:
//	- application/json
//
//	Schemes: https
//
//	Security:
//	  JWT:
//
//	Responses:
//	  200:
//	  403: errorResponse
//	  400: errorResponse
func (h *EVSTHandler) delete(c *fiber.Ctx) error {
	ctx := c.UserContext()
	c.Accepts("application/json")

	fileID, err := strconv.Atoi(c.Params("file_id"))
	if err != nil {
		log.L(ctx).Error("unable to convert file_id to number", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusBadRequest,
			Message:    "unable to convert file_id to number",
		}
		return herr.WriteToResponse(c)
	}

	_, teamID, err := h.getTokenAndTeamID(ctx, c)
	if err != nil {
		return err
	}

	if err := h.s.DeleteEvidence(ctx, &domain.DeleteEvidenceServiceInput{
		FileID: fileID,
		TeamID: teamID,
	}); err != nil {
		log.L(ctx).Error("unable to delete file", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusBadRequest, Message: "unable to delete file",
		}
		return herr.WriteToResponse(c)
	}

	return nil
}

// listEvidenceByContext gets a list of fileIDs for a context query.
//
// swagger:route POST /evidence/list evidence ListEvidenceAction
//
// Get a list of processes for specific queries.
//
//	Consumes:
//	- application/json
//
//	Produces:
//	- application/json
//
//	Schemes: https
//
//	Security:
//	  JWT:
//
//	Responses:
//	  200: listEvidenceView
//	  403: errorResponse
//	  400: errorResponse
func (h *EVSTHandler) listEvidenceByContext(c *fiber.Ctx) error {
	ctx := c.UserContext()
	c.Accepts("application/json")

	_, teamID, err := h.getTokenAndTeamID(ctx, c)
	if err != nil {
		return err
	}

	var allContext domain.ListEvidenceInput
	if err := c.BodyParser(&allContext.Body); err != nil {
		log.L(ctx).Error("parse body of the request", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusBadRequest,
			Message:    "invalid request",
		}
		return herr.WriteToResponse(c)
	}

	validatedIn, err := json.Marshal(allContext.Body)
	if err != nil {
		log.L(ctx).Error("marshal input failed", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusBadRequest,
			Message:    "invalid request",
		}
		return herr.WriteToResponse(c)
	}

	attestations, err := h.s.ListReports(ctx, (*json.RawMessage)(&validatedIn), teamID)
	if err != nil {
		log.L(ctx).Error("get requested processes", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusBadRequest, Message: "unable get a list of processes",
		}
		return herr.WriteToResponse(c)
	}

	output := domain.ListEvidenceViewOutputBody{
		Evidences: attestations,
	}

	return c.JSON(output)
}

func (h *EVSTHandler) getTokenAndTeamID(
	ctx context.Context,
	c *fiber.Ctx,
) (tokenStr string, teamID int64, err error) {
	m := c.GetReqHeaders()
	tokenStr = strings.TrimPrefix(m["Authorization"], "Bearer ")

	// get the team ID from the m2m token subject
	teamID, err = h.s.GetTeamID(ctx, &tokenStr)
	if errors.Is(err, domain.ErrSQLEmptyRecord) {
		log.L(ctx).Error("teamID doesn't exist in DB", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusForbidden,
			Message:    "unauthorized",
		}
		return "", 0, herr.WriteToResponse(c)
	} else if err != nil {
		log.L(ctx).Error("unable to get team ID from token", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusBadRequest,
			Message:    "internal error",
		}
		return "", 0, herr.WriteToResponse(c)
	}
	return tokenStr, teamID, nil
}
