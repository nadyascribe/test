package domain

import "context"

type CallUploadEvidenceInput struct {
	UploadEvidenceInternal
	ScribeURL string
	Bom       []byte
}

type CallFinishEvidenceInput struct {
	FinishUploadEvidenceWithTeamID
	ScribeURL string
}

// EvidenceStoreClient is the interface for the evidence store client
//
//go:generate mockgen -destination=mocks/mock_evidence_store_client.go -package=mocks . EvidenceStoreClient
type EvidenceStoreClient interface {
	CallUploadEvidence(
		ctx context.Context, in *CallUploadEvidenceInput,
	) (out *CreateEvidenceOutput, err error)

	CallFinishEvidence(
		ctx context.Context, in *CallFinishEvidenceInput,
	) error

	UploadFileToS3(
		ctx context.Context, presignedURL string, marshaledBom []byte,
	) error
}
