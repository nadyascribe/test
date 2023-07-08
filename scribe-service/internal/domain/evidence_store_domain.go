package domain

import (
	"encoding/json"
	"errors"

	cocosign "github.com/scribe-security/cocosign/storer/evidence"
)

// IMPORTANT NOTE:
// The Evidence Store service is not a standalone service, it is a part of the file transfer service.
// Evidence Store provides a new /evidence endpoint for uploading evidence via the file transfer service.

// UploadEvidence action parameters
type UploadEvidence struct {
	// Key is a file name path, it should be uniq
	Key string `json:"key"`

	// ContentType file content type
	ContentType string `json:"content_type"`

	// ContextType file context type
	ContextType string `json:"context_type"`

	// Context additional file metadata
	ContextData json.RawMessage `json:"context"`
}

// UploadEvidenceInput represents parameters of create file transfer action
// This object contains details about file which we will transfer to cloud storage.
//
// swagger:parameters uploadEvidenceAction
type UploadEvidenceInput struct {
	// in: body
	Body UploadEvidence
}

// FinishFileTransferInput represents parameters for finish file transfer action
//
// Contains result of file content PUT through presigned URL.
//
// swagger:parameters finishUploadEvidenceAction
type FinishUploadEvidenceInput struct {
	// in: body
	Body FinishUploadEvidence
}

type FinishUploadEvidence struct {
	// FileID of transfer, can be used to link with other objects
	FileID int `json:"file_id"`

	// Error message, if not nil, transfer will be marked as failed
	Error *string `json:"error"`
}

// used for internal handler and functions
type FinishUploadEvidenceWithTeamID struct {
	// FileID of transfer, can be used to link with other objects
	FileID int `json:"file_id"`

	// Error message, if not nil, transfer will be marked as failed
	Error *string `json:"error"`

	// TeamID is not part of the request and set by handler.
	TeamID int64 `json:"team_id"`
}

// DownloadEvidenceInput contains parameters required to get file download URL.
// Represents parameters to get file download URL by file_id.
//
// swagger:parameters downloadEvidenceAction
type DownloadEvidenceInput struct {
	// FileID if not null used to delete only one file
	// in: path
	FileID *int `json:"file_id"`
}

// ListEvidenceInput represents query parameters requested by the front-end.
// Contains the possible query parameters a user might search with for reports
//
// swagger:parameters ListEvidenceAction
type ListEvidenceInput struct {
	// in: body
	Body cocosign.AllContext
}

// ListEvidenceViewOutput details a list of the queried evidence
//
// swagger:response listEvidenceView
type ListEvidenceViewOutput struct {
	// in: body
	Body struct {
		Evidences []Attestation `json:"evidences"`
	}
}

type ListEvidenceViewOutputBody struct {
	Evidences []Attestation `json:"evidences"`
}

// type AttestationList []Attestation

// UploadEvidenceInternal in the input for the internal upload evidence handler
type UploadEvidenceInternal struct {
	// Key is a file name path, it should be uniq
	Key string `json:"key"`

	// TeamID is the original user id that uploaded the file
	TeamID int64 `json:"team_id"`

	// ContentType file content type
	ContentType string `json:"content_type"`

	// ContextType file context type
	ContextType string `json:"context_type"`

	// Context additional file metadata
	ContextData json.RawMessage `json:"context"`
}

var (
	// ErrSQLEmptyRecord used by File Transfer service to indicate file doesnt exist
	ErrSQLEmptyRecord = errors.New("empty record")

	// ErrFileTransferAccessDenied used by File Transfer service to indicate that user
	// has not righs to access to that file
	ErrFileTransferAccessDenied = errors.New("access denied")
)

// UploadEvidenceFileTransfer action parameters
type UploadEvidenceFileTransfer struct {
	// Key is a file name path, it should be uniq
	Key string `json:"key"`

	// TeamID is not part of the request and set by handler.
	TeamID int64 `json:"-"`

	// ContentType file content type
	ContentType string `json:"content_type"`

	// ContextType file context type
	ContextType string `json:"context_type"`

	// Context additional file metadata
	ContextData json.RawMessage `json:"context"`
}

// PGCreateEvidenceInput represents parameters of create evidence repository input
type PGCreateEvidenceInput struct {
	// Key is a file name path, it should be uniq
	Key string `json:"key"`

	// TeamID is not part of the request and set by handler.
	TeamID int64 `json:"-"`

	// ContentType file content type
	ContentType string `json:"content_type"`

	// ContextType file context type
	ContextType string `json:"context_type"`

	// Context additional file metadata
	ContextData json.RawMessage `json:"context"`

	// PipelineRun is the pipeline run id
	PipelineRun int64 `json:"pipeline_run"`

	// TargetName is the target name of the attestation
	TargetName string `json:"target_name"`

	// TargetType is the target type of the attestation, must be a value from the TargetType table
	TargetType string `json:"target_type"`
}

// FileTransferAttributes determined by the FileTransferService
type FileTransferAttributes struct {
	// Bucket name
	Bucket string `json:"bucket"`

	// CloudStorage name: example 's3'
	CloudStorage string `json:"cloud_storage"`
}

// DeleteEvidenceInput contains filters values to delete files.
// Represents parameters to delete file by file_id or files by key pattern.
//
// swagger:parameters deleteEvidenceAction
type DeleteEvidenceInput struct {
	// FileID if not null used to delete only one file
	// in: path
	FileID *int `json:"file_id"`
}

// DeleteEvidenceRepoInput contains filters values to delete files for the DB.
// Represents parameters to delete file by file_id or files by key pattern.
type DeleteEvidenceRepoInput struct {
	// FileID if not null used to delete only one file
	FileID *int `json:"file_id"`

	// Key pattern to delete all files matched to it, this field ignored if "file_id" is set
	Key *string `json:"key"`

	// TeamID to limit access to delete file.
	TeamID int64 `json:"-"`
}

// DeleteEvidenceServiceInput contains filters values to delete files.
//
// Represents parameters to delete file by file_id or files by key pattern.
type DeleteEvidenceServiceInput struct {
	// FileID if not null used to delete only one file
	FileID int `json:"file_id"`

	// TeamID to limit access to delete file.
	TeamID int64 `json:"-"`
}

// CreateEvidenceOutput response for CreateEvidence request
//
// swagger:response createEvidenceOutput
type CreateEvidenceOutput struct {
	// in: body
	CreateEvidenceOutputBody
}

type CreateEvidenceOutputBody struct {
	// FileID for the internal objects link
	FileID int `json:"file_id"`

	// PresignedURL to upload the file directly to the cloud storage
	PresignedURL string `json:"presigned_url"`
}

// GetEvidenceDownloadInput parameters to build download URL.
type GetEvidenceDownloadInput struct {
	// FileID if not null used to delete only one file
	FileID int `json:"file_id"`

	// TeamID to limit access to downloaded file.
	TeamID int64 `json:"-"`
}

// GetEvidenceDownloadOutput response for getEvidenceDownloadOutput request.
//
// swagger:response getEvidenceDownloadOutput
type GetEvidenceDownloadOutput struct {
	// in: body
	GetEvidenceDownloadOutputBody
}

type GetEvidenceDownloadOutputBody struct {
	// PresignedURL to download the file directly from the cloud storage
	PresignedURL string `json:"presigned_url"`
}

type MixapanelProperties struct {
	Key   string
	Value string
}

// Token type received from network for mixpanel event
type MixapanelTokenType string

const (
	MixpanelTokenGensbom  MixapanelTokenType = "gensbom"
	MixpanelTokenFrontend MixapanelTokenType = "frontend"
)

type SendMixpanelEventInputs struct {
	// MixPanel EventName
	EventName string

	// MixPanel custom information
	Properties []MixapanelProperties

	// User JWT token
	UserToken string

	// Token type
	TokenType MixapanelTokenType

	// User IP
	IP string
}
