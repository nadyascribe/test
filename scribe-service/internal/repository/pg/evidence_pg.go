package repository

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"strings"

	"github.com/jmoiron/sqlx"
	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/internal/db"
	"github.com/scribe-security/scribe2/scribe-service/internal/domain"
	"github.com/scribe-security/scribe2/scribe-service/pkg/errors"
	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

const (
	statusCreated  = "created"
	statusUploaded = "uploaded"
	statusFailed   = "failed"
)

// PgRespository defines data access layer over PostgreSQL database
type PgRespository struct {
	conn *sqlx.DB
	db   *db.Queries
}

// NewPgEvidenceRepository will create an object that represent the X interface
func NewPgEvidenceRepository(conn *sqlx.DB) domain.EvidenceStoreRepository {
	r := &PgRespository{
		conn: conn,
		db:   db.New(conn.DB),
	}

	return r
}

// CreateEvidence record in the database, with context.
// If we already have record for same file we overwrite it.
// Returns fileID of the created record.
func (r *PgRespository) CreateEvidence(
	ctx context.Context, in *domain.PGCreateEvidenceInput,
) (int, error) {
	l := log.L(ctx).Logger().With(zap.String("key", in.Key), zap.Int64("userID", in.TeamID))

	// check if we already have file with the same key
	ret, err := r.db.GetEvidenceByKey(ctx, &in.Key)
	// found file with the same key
	if err == nil {
		// check if it belongs to the same user
		if *ret.TeamId == in.TeamID {
			l.Info("file already exists and belongs to the same user, try to delete it")
			if err := r.db.DeleteEvidence(ctx, db.DeleteEvidenceParams{Teamid: in.TeamID, ID: ret.ID}); err != nil {
				l.Error("delete existed transfer file", zap.Error(err))
				return 0, err
			}
		} else {
			l.Info("file already exists and belongs to another user, will not delete it")
			return 0, errors.New("file with this key already exists and belongs to another user")
		}

		l.Info("deleted duplicate file, will rewrite with new file")
	}

	// create file transfer record with context data (metadata)
	fileObject, err := r.db.CreateEvidence(ctx, db.CreateEvidenceParams{
		Key:         &in.Key,
		Teamid:      in.TeamID,
		Contenttype: in.ContentType,
		Contexttype: in.ContextType,
		Context:     in.ContextData,
		Pipelinerun: in.PipelineRun,
		Targettype:  in.TargetType,
		Targetname:  in.TargetName,
	})
	if err != nil {
		l.Error("create transfer file record", zap.Error(err),
			zap.String("in.ContentType", in.ContentType),
			zap.String("targetType", in.TargetType))
		return 0, err
	}

	return int(fileObject.ID), nil
}

// FinishUploadEvidence set uploaded status for created evidence upload
// It will return error if evidence has any other status then 'created'.
func (r *PgRespository) FinishUploadEvidence(
	ctx context.Context,
	in *domain.FinishUploadEvidenceWithTeamID,
) error {
	l := log.L(ctx).Logger().With(zap.Int("file_id", in.FileID), zap.Int64("userID", in.TeamID))
	file, err := r.db.GetEvidenceByFileID(ctx, int64(in.FileID))
	if err != nil {
		l.Error("get file transfer by file id", zap.Error(err))
		return err
	}

	if file.TeamId == nil || *file.TeamId != in.TeamID {
		l.Error("creator and finisher user_id mismatch")
		return fmt.Errorf("unauthorized request to finish this file upload")
	}

	if file.TeamId == nil || *file.TeamId != in.TeamID {
		l.Error("creator and finisher team_id mismatch")
		return fmt.Errorf("unauthorized request to finish this file upload")
	}

	if file.State != statusCreated {
		l.Error("wrong status to finish transfer", zap.String("status", file.State))
		return fmt.Errorf("existed status of file transfer is not 'created'")
	}

	update := db.SetEvidenceStateParams{
		State: statusUploaded,
		ID:    int64(in.FileID),
	}

	if in.Error != nil && *in.Error != "" {
		update.State = statusFailed
	}

	if err := r.db.SetEvidenceState(ctx, update); err != nil {
		l.Error("set evidence status", zap.Error(err))
		return err
	}

	return nil
}

// DeleteEvidence by key pattern or one file by file_id
// returns domain.ErrFileTransferAccessDenied if file belongs to another user
func (r *PgRespository) DeleteEvidence(
	ctx context.Context, in *domain.DeleteEvidenceRepoInput,
) error {
	l := log.L(ctx).Logger().With()
	if in.FileID == nil && in.Key == nil {
		return fmt.Errorf("file_id or key pattern can't both be nil")
	}
	if in.FileID != nil {
		l = l.With(zap.Int("file_id", *in.FileID))
	} else {
		l = l.With(zap.String("key", *in.Key))
	}

	// check if user has access to delete file
	attest, err := r.GetEvidenceByID(ctx, *in.FileID)
	if err != nil {
		l.Error("get file transfer by file id", zap.Error(err))
		return err
	}

	if attest.TeamID == nil {
		l.Error("attestation doesn't have teamId")
		return domain.ErrFileTransferAccessDenied
	}

	if *attest.TeamID != in.TeamID {
		l.Error("team doesn't have access to delete file")
		return domain.ErrFileTransferAccessDenied
	}

	queryParams := db.DeleteEvidenceParams{
		Teamid: in.TeamID,
	}
	if in.FileID != nil {
		queryParams.ID = int64(*in.FileID)
	} else {
		queryParams.Key = *in.Key
	}

	if err := r.db.DeleteEvidence(ctx, queryParams); err != nil {
		l.Error("delete file transfers", zap.Error(err))
		return err
	}

	return nil
}

// GetEvidenceByID queries file transfer object by file_id
// if empty record, returns error domain.ErrSQLEmptyRecord
func (r *PgRespository) GetEvidenceByID(
	ctx context.Context, fileID int,
) (*domain.Attestation, error) {
	out, err := r.db.GetEvidenceByFileID(ctx, int64(fileID))
	if err == sql.ErrNoRows {
		log.L(ctx).Error("file object not found", zap.Int("file_id", fileID))
		return nil, domain.ErrSQLEmptyRecord
	} else if err != nil {
		log.L(ctx).Error(
			"error query file object by id form database",
			zap.Error(err),
			zap.Int("file_id", fileID))
		return nil, err
	}

	return dbEvidenceObjectToDomainObject(&out), nil
}

// GetEvidenceByKey returns evidence record by key
// if empty record, returns error domain.ErrSQLEmptyRecord
func (r *PgRespository) GetEvidenceByKey(
	ctx context.Context, key string,
) (*domain.Attestation, error) {
	l := log.L(ctx).Logger().With(zap.String("key", key))
	e, err := r.db.GetEvidenceByKey(ctx, &key)
	if err == sql.ErrNoRows {
		log.L(ctx).Info("file object not found", zap.String("key", key))
		return nil, domain.ErrSQLEmptyRecord
	} else if err != nil {
		l.Error("get evidence by key", zap.Error(err))
		return nil, err
	}

	return dbEvidenceObjectToDomainObject(&e), nil
}

// dbEvidenceObjectToDomainObject convert internal Evidence object to domain type
func dbEvidenceObjectToDomainObject(
	in *db.OsintAttestation,
) *domain.Attestation {
	domainObj := &domain.Attestation{
		ID:          in.ID,
		ContentType: in.ContentType,
		TargetType:  in.TargetType,
		TargetName:  in.TargetName,
		ContextType: in.ContextType,
		Context:     in.Context,
		Key:         in.Key,
		Timestamp:   in.Timestamp,
		UserID:      in.UserId,
		TeamID:      in.TeamId,
		PipelineRun: in.PipelineRun,
		State:       domain.Typeevidencestatus(in.State),
		SigStatus:   in.SigStatus,
		Alerted:     in.Alerted,
		License:     in.License,
		Deleted:     in.Deleted,
		Txt:         in.Txt,
		JobIds:      in.JobIds,
	}

	return domainObj
}

// dbEvidenceObjectToDomainObject convert internal Evidence object to domain type
func dbListEvidenceRowObjectToDomainObject(
	in *db.ListEvidenceRow,
) *domain.Attestation {
	domainObj := &domain.Attestation{
		ID:          in.ID,
		ContentType: in.ContentType,
		ContextType: in.ContextType,
		Context:     in.Context,
		Key:         in.Key,
		Timestamp:   in.Timestamp,
		UserID:      in.UserId,
		TeamID:      in.TeamId,
		License:     in.License,
		Txt:         in.Txt,
		State:       domain.Typeevidencestatus(in.State),
	}

	return domainObj
}

// UpdateContext updates the context for a given fileID
func (r *PgRespository) UpdateContext(
	ctx context.Context, fileID int, valintContext *json.RawMessage,
) error {
	if err := r.db.UpdateContext(ctx, db.UpdateContextParams{
		Context: *valintContext,
		ID:      int64(fileID),
	}); err != nil {
		log.L(ctx).Error(
			"error update file transfer context by id from database",
			zap.Error(err),
			zap.Int("file_id", fileID))
		return err
	}

	return nil
}

// GetTeamIDByTokenSub gets the teamID for the input subject from token
// returns error=domain.ErrSQLEmptyRecord if team not found
func (r *PgRespository) GetTeamIDByTokenSub(
	ctx context.Context, subjectFromToken string,
) (teamID int64, err error) {
	// trim "@clients" from subject
	subjectFromToken = strings.TrimSuffix(subjectFromToken, "@clients")

	team, err := r.db.GetTeamByClientID(ctx, &subjectFromToken)
	if err == sql.ErrNoRows {
		return 0, domain.ErrSQLEmptyRecord
	}
	if err != nil {
		log.L(ctx).Error(
			"error query user by token sub from database",
			zap.Error(err),
			zap.String("subjectFromToken", subjectFromToken))
		return 0, err
	}

	return *team.ID, nil
}

// ListEvidence
func (r *PgRespository) ListEvidence(
	ctx context.Context, queryJSON *json.RawMessage, teamID int64,
) ([]domain.Attestation, error) {
	attests, err := r.db.ListEvidence(ctx, db.ListEvidenceParams{
		Input:  *queryJSON,
		Teamid: teamID,
	})
	if err != nil {
		return nil, err
	}
	if len(attests) == 0 {
		log.L(ctx).Info("no evidence found", zap.Int64("input userID", teamID))
		return nil, nil
	}

	// convert to domain object
	attestations := make([]domain.Attestation, 0, len(attests))
	for i := range attests {
		attestations = append(attestations, *dbListEvidenceRowObjectToDomainObject(&attests[i]))
	}

	return attestations, nil
}

func dbPipelineRunObjectToDomainObject(in *db.OsintPipelineRun) *domain.PipelineRunObj {
	domainObj := &domain.PipelineRunObj{
		ID:           in.ID,
		ProductKey:   in.ProductKey,
		PipelineName: in.PipelineName,
		PipelineRun:  in.PipelineRun,
		Context:      in.Context,
		Version:      in.Version,
		Timestamp:    in.Timestamp.Time,
		Team:         in.Team,
		Deleted:      in.Deleted,
	}
	return domainObj
}

// GetPipelineRun returns the pipelinerun for the productKey, pipelineName, pipelineRun, version and team
func (r *PgRespository) GetPipelineRun(
	ctx context.Context, in *domain.GetPipelineRunInput,
) (*domain.PipelineRunObj, error) {
	if in == nil {
		return nil, errors.New("input is nil")
	}
	pipelineRunObj, err := r.db.GetPipelineRun(ctx, db.GetPipelineRunParams{
		Productkey:   in.ProductKey,
		Pipelinename: in.PipelineName,
		Pipelinerun:  in.PipelineRun,
		Team:         in.TeamID,
	})
	if err != nil {
		return nil, err
	}

	return dbPipelineRunObjectToDomainObject(&pipelineRunObj), nil
}

// GetPipelineRun returns the pipelinerun for the productKey, pipelineName, pipelineRun and team
func (r *PgRespository) GetPipelineRunByGitURLs(
	ctx context.Context, gitURLs ...string,
) (*domain.PipelineRunObj, error) {
	pipelineRunObj, err := r.db.GetPipelineRunByGitURL(ctx, gitURLs)
	if err != nil {
		return nil, err
	}

	return dbPipelineRunObjectToDomainObject(&pipelineRunObj), nil
}

func (r *PgRespository) DisableGithubInstallation(
	ctx context.Context, installationID int64,
) error {
	err := r.db.DisableGithubInstallation(ctx, installationID)
	return errors.Wrap(err)
}

func (r *PgRespository) EnableGithubInstallation(
	ctx context.Context, installationID int64,
) error {
	err := r.db.EnableGithubInstallation(ctx, installationID)
	return errors.Wrap(err)
}

// CreatePipelineRun creates a new pipelinerun in the database and returns the pipelinerun object
func (r *PgRespository) CreatePipelineRun(
	ctx context.Context, pipelineRun *domain.PipelineRunObj,
) (*domain.PipelineRunObj, error) {
	pipelineRunObj, err := r.db.CreatePipelineRun(ctx, db.CreatePipelineRunParams{
		Productkey:   pipelineRun.ProductKey,
		Pipelinename: pipelineRun.PipelineName,
		Pipelinerun:  pipelineRun.PipelineRun,
		Context:      *pipelineRun.Context,
		Version:      pipelineRun.Version,
		Team:         pipelineRun.Team,
	})
	if err != nil {
		return nil, err
	}

	return dbPipelineRunObjectToDomainObject(&pipelineRunObj), nil
}

// CreateProduct creates a new product in the database and returns the product object
// input ID will be ignored, chosen by DB
func (r *PgRespository) CreateProduct(
	ctx context.Context, in *domain.Product,
) (*domain.Product, error) {
	if in == nil {
		return nil, fmt.Errorf("input is empty")
	}

	productObj, err := r.db.CreateProduct(ctx, db.CreateProductParams{
		Name:           in.Name,
		Teamid:         in.TeamID,
		Key:            in.Key,
		Userdefinedkey: in.UserDefinedKey,
	})
	if err != nil {
		return nil, err
	}

	return &domain.Product{
		ID:             *productObj.ID,
		Name:           productObj.Name,
		TeamID:         productObj.TeamId,
		Key:            productObj.Key,
		UserDefinedKey: *productObj.UserDefinedKey,
	}, nil
}

// GetProduct returns the product for the productKey and teamID
func (r *PgRespository) GetProduct(
	ctx context.Context, userProductKey string, teamID int64,
) (*domain.Product, error) {
	productObj, err := r.db.GetProduct(ctx, db.GetProductParams{
		Userdefinedkey: userProductKey,
		Teamid:         teamID,
	})
	if err == sql.ErrNoRows {
		log.L(ctx).Info("product object not found", zap.String("userProductKey", userProductKey))
		return nil, domain.ErrSQLEmptyRecord
	} else if err != nil {
		log.L(ctx).Error(
			"DB error while getting product object",
			zap.Error(err),
			zap.String("userProductKey", userProductKey))
		return nil, err
	}

	return &domain.Product{
		ID:             *productObj.ID,
		Name:           productObj.Name,
		TeamID:         productObj.TeamId,
		Key:            productObj.Key,
		UserDefinedKey: *productObj.UserDefinedKey,
	}, nil
}
