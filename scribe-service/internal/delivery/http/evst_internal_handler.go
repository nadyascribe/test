package http

import (
	"net/http"

	"github.com/gofiber/fiber/v2"
	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/internal/domain"
	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
	"github.com/scribe-security/scribe2/scribe-service/pkg/transport"
)

// EVSTInternalHandler serves all requests for upload and manage files to a cloud storages
type EVSTInternalHandler struct {
	s domain.EvidenceStoreService
}

// NewEVSTHandler instance constructor
func NewEVSTInternalHandler(r fiber.Router,
	s domain.EvidenceStoreService,
) *EVSTInternalHandler {
	handler := &EVSTInternalHandler{
		s: s,
	}
	r.Post("/", handler.uploadEvidenceInternal)
	r.Post("/finish", handler.finishUploadEvidenceInternal)
	return handler
}

// uploadEvidenceInternal returns the presignedURL for a new evidence context
// POST /internal/evidence/
func (h *EVSTInternalHandler) uploadEvidenceInternal(c *fiber.Ctx) error {
	ctx := c.UserContext()
	c.Accepts("application/json")

	var in domain.UploadEvidenceInternal
	if err := c.BodyParser(&in); err != nil {
		log.L(ctx).Error("parse body of the request", zap.Error(err))
		return err
	}

	out, err := h.s.CreateEvidence(ctx, &domain.UploadEvidenceFileTransfer{
		Key:         in.Key,
		TeamID:      in.TeamID,
		ContentType: in.ContentType,
		ContextType: in.ContextType,
		ContextData: in.ContextData,
	})
	if err != nil {
		log.L(ctx).Error("unable to get presigned URL", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusBadRequest,
			Message:    "unable to get presigned URL",
		}
		return herr.WriteToResponse(c)
	}

	return c.JSON(out)
}

// Mark file transfer as finished.
// Called after file content PUT to presignedURL.
// POST /internal/evidence/finish
func (h *EVSTInternalHandler) finishUploadEvidenceInternal(c *fiber.Ctx) error {
	ctx := c.UserContext()
	c.Accepts("application/json")

	var in domain.FinishUploadEvidenceWithTeamID
	if err := c.BodyParser(&in); err != nil {
		log.L(ctx).Error("parse body of the request", zap.Error(err))
		return err
	}

	if err := h.s.FinishEvidenceFileTransfer(ctx, &domain.FinishUploadEvidenceWithTeamID{
		FileID: in.FileID,
		Error:  in.Error,
		TeamID: in.TeamID,
	}); err != nil {
		log.L(ctx).Error("unable to finish upload", zap.Error(err))
		herr := &transport.ResponseError{
			HTTPStatus: http.StatusBadRequest, Message: "unable set finish status",
		}
		return herr.WriteToResponse(c)
	}

	return nil
}
