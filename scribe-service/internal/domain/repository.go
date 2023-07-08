package domain

import (
	"context"
	"database/sql"
	"encoding/json"
	"time"
)

// EvidenceStoreRepository defines data access layer
//
//go:generate mockgen -destination=mocks/mock_repository.go -package=mocks . EvidenceStoreRepository
type EvidenceStoreRepository interface {
	// CreateEvidence record in the database, with context.
	// If we already have record for same file we overwrite it.
	// Returns fileID of the created record.
	CreateEvidence(ctx context.Context, in *PGCreateEvidenceInput) (int, error)

	// FinishUploadEvidence set uploaded status for created evidence upload
	// It will return error if evidence has any other status then 'created'.
	FinishUploadEvidence(ctx context.Context, in *FinishUploadEvidenceWithTeamID) error

	// DeleteEvidence by key pattern or one file by file_id
	// returns domain.ErrFileTransferAccessDenied if file belongs to another user
	DeleteEvidence(ctx context.Context, in *DeleteEvidenceRepoInput) error

	// GetEvidenceByID queries file transfer object by file_id
	// if empty record, returns error domain.ErrSQLEmptyRecord
	GetEvidenceByID(ctx context.Context, fileID int) (*Attestation, error)

	// GetEvidenceByKey returns evidence record by key
	// if empty record, returns error domain.ErrSQLEmptyRecord
	GetEvidenceByKey(ctx context.Context, key string) (*Attestation, error)

	// UpdateContext updates the context for a given fileID
	UpdateContext(ctx context.Context, fileID int, context *json.RawMessage) error

	// GetTeamIDByTokenSub gets the teamID for the input subject from token
	// returns error=domain.ErrSQLEmptyRecord if team not found
	GetTeamIDByTokenSub(ctx context.Context, subjectFromToken string) (teamID int64, err error)

	// ListEvidence
	ListEvidence(ctx context.Context, queryJSON *json.RawMessage, userID int64) ([]Attestation, error)

	// GetPipelineRun returns the pipelineRun for the productKey, pipelineName, pipelineRun and team
	GetPipelineRun(ctx context.Context, in *GetPipelineRunInput,
	) (*PipelineRunObj, error)

	// GetPipelineRunByGitURL returns the pipelineRun for the gitURL
	GetPipelineRunByGitURLs(
		ctx context.Context, gitURLs ...string,
	) (*PipelineRunObj, error)

	EnableGithubInstallation(
		ctx context.Context, installationID int64,
	) error

	DisableGithubInstallation(
		ctx context.Context, installationID int64,
	) error

	// CreatePipelineRun creates a new pipelinerun in the database and returns the pipelinerun object
	CreatePipelineRun(ctx context.Context, pipelineRun *PipelineRunObj) (*PipelineRunObj, error)

	// CreateProduct creates a new product in the database and returns the product object
	// input ID will be ignored, chosen by DB
	CreateProduct(ctx context.Context, in *Product) (*Product, error)

	// GetProduct returns the product for the productKey and teamID
	// If no product exists, returns domain.ErrSQLEmptyRecord
	GetProduct(ctx context.Context, userProductKey string, teamID int64) (*Product, error)
}

type Attestation struct {
	ID          int64              `json:"id"`
	ContentType string             `json:"contenttype"`
	TargetType  string             `json:"targettype"`
	TargetName  string             `json:"targetname"`
	ContextType string             `json:"contexttype"`
	Context     json.RawMessage    `json:"context"`
	Key         *string            `json:"key"`
	Timestamp   sql.NullTime       `json:"timestamp"`
	UserID      *int64             `json:"userid"`
	TeamID      *int64             `json:"teamid"`
	PipelineRun int64              `json:"pipelinerun"`
	State       Typeevidencestatus `json:"state"`
	SigStatus   *string            `json:"sigstatus"`
	Alerted     *bool              `json:"alerted"`
	License     *string            `json:"license"`
	Deleted     *bool              `json:"deleted"`
	Txt         interface{}        `json:"txt"`
	JobIds      []string           `json:"job_ids"`
}

type Typeevidencestatus string

const (
	TypeevidencestatusCreated  Typeevidencestatus = "created"
	TypeevidencestatusUploaded Typeevidencestatus = "uploaded"
	TypeevidencestatusFailed   Typeevidencestatus = "failed"
	TypeevidencestatusRemoved  Typeevidencestatus = "removed"
)

type OsintSignatureStatus string

type NullOsintSignatureStatus struct {
	OsintSignatureStatus OsintSignatureStatus
	Valid                bool // Valid is true if OsintSignatureStatus is not NULL
}

type UserObject struct {
	ID            int64           `json:"id"`
	Sub           string          `json:"sub"`
	Aud           string          `json:"aud"`
	FirstLogin    time.Time       `json:"firstlogin"`
	LastLogin     time.Time       `json:"lastlogin"`
	UpdatedAt     time.Time       `json:"updatedat"`
	TeamInvites   int64           `json:"teaminvites"`
	Locale        string          `json:"locale"`
	BetaUser      bool            `json:"betauser"`
	GivenName     string          `json:"givenname"`
	LastName      string          `json:"lastname"`
	Picture       string          `json:"picture"`
	NickName      string          `json:"nickname"`
	Email         string          `json:"email"`
	EmailVerified bool            `json:"emailverified"`
	Settings      json.RawMessage `json:"settings"`
	Deleted       bool            `json:"deleted"`
}

type PipelineRunObj struct {
	ID           int64            `json:"id"`
	ProductKey   string           `json:"productkey"`
	PipelineName string           `json:"pipelinename"`
	PipelineRun  string           `json:"pipelinerun"`
	Context      *json.RawMessage `json:"context"`
	Version      string           `json:"version"`
	Timestamp    time.Time        `json:"timestamp"`
	Team         int64            `json:"team"`
	Deleted      *bool            `json:"deleted"`
}

type GetPipelineRunInput struct {
	ProductKey   string
	PipelineName string
	PipelineRun  string
	TeamID       int64
}

// if the product does not exist, a new product is created with
// name = first non-empty value is taken from the context: name, git_url, image_name, target_git_url, dir_path, file_path
// key = the UUID generated from the product-key
// userDefinedKey = the actual product-key, that the UUID was generated from
// teamId = team id corresponding to the provided clientId
type Product struct {
	ID             int64  `json:"id"` // ID generated by database
	Name           string `json:"name"`
	TeamID         int64  `json:"teamId"`
	Key            string `json:"key"`
	UserDefinedKey string `json:"userDefinedKey"`
}
