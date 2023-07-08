//nolint:gofumpt
package domain

import (
	"context"
	"encoding/json"
	"errors"
)

// EvidenceStoreService defines logic layer
//
//go:generate mockgen -destination=mocks/mock_service.go -package=mocks . EvidenceStoreService
type EvidenceStoreService interface {
	// GetTeamName returns user team name from token
	GetTeamName(ctx context.Context, token *string) (string, error)

	// GetTeamID returns the team ID for the m2m jwt subject if team exists in DB
	// returns error=domain.ErrSQLEmptyRecord if team not found
	GetTeamID(ctx context.Context, token *string) (teamID int64, err error)

	// CreateEvidence invokes cloud storage presign URL call and returns this URL.
	// If the user input flags in valint are invalid, returns error domain.ErrInvalidPipelineParams.
	CreateEvidence(ctx context.Context, in *UploadEvidenceFileTransfer) (*CreateEvidenceOutputBody, error)

	// get presigned URL from cloud storage and the s3 attributes
	GetPresignedURLandAttrs(ctx context.Context, key string) (presignedURL string, err error)

	// FinishEvidenceFileTransfer by FileID and update status in the database.
	FinishEvidenceFileTransfer(ctx context.Context, in *FinishUploadEvidenceWithTeamID) error

	// DeleteEvidence by key pattern or one file by fileID.
	// returns domain.ErrFileTransferAccessDenied if file belongs to another user
	DeleteEvidence(ctx context.Context, in *DeleteEvidenceServiceInput) error

	// GetEvidenceDownload returns presigned URL for download by fileID.
	GetEvidenceDownload(ctx context.Context, in *GetEvidenceDownloadInput) (*GetEvidenceDownloadOutputBody, error)

	// SendMixpanelEvent sends an event with a given name and properties to mix panel,
	// with the user email as the mixpanel distinctID.
	// The email is extracted by getting the projectID, querying the projects table for the auth0 OwnerID
	// and getting the user info from auth0.
	SendMixpanelEvent(ctx context.Context, in *SendMixpanelEventInputs) error

	// ListReports reuturs a list of process states for given query.
	ListReports(ctx context.Context, queryJSON *json.RawMessage, userID int64) ([]Attestation, error)

	TriggerETL(ctx context.Context, payload TriggerETLPayload) error

	GetLastPipelineRunForRepos(ctx context.Context, repos ...string) (*PipelineRunObj, error)

	DisableGithubInstallation(ctx context.Context, installationID int64) error
	EnableGithubInstallation(ctx context.Context, installationID int64) error
}

var ErrInvalidPipelineParams = errors.New("invalid pipeline params")
var ErrInvalidProductKey = errors.New("invalid product key param")
