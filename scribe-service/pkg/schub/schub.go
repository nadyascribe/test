package schub

import (
	"context"
	"encoding/json"

	"go.uber.org/zap/zapcore"

	"github.com/scribe-security/scribe2/scribe-service/internal/domain"
)

// BuildIntegrity API type
type BuildIntegrity string

const (
	BuildUnknow         BuildIntegrity = "Unknow"
	BuildModified       BuildIntegrity = "Modified"
	BuildInProgress     BuildIntegrity = "In Progress"
	BuildValidated      BuildIntegrity = "Validated"
	BuildNotApplicable  BuildIntegrity = "N/A"
	SignedAnalyzeFailed BuildIntegrity = "Signed File Analyze Failed"
)

// Verification status type
type Verification string

const (
	VerificationStarted Verification = "Verification Started"
	VerificationSuccess Verification = "Verification Success"
	VerificationFailed  Verification = "Verification Failed"
)

// ScribeHubConnector interface to access to Scribe Hub
//
//go:generate mockgen -destination=mocks/mock_scribe_hub_connector.go -package=mocks . ScribeHubConnector
type ScribeHubConnector interface {
	SendBuildInfo(ctx context.Context, in *BuildInfo) error
	SendCVEInfo(ctx context.Context, in *CVEInfo) error
	SendScoreCardInfo(ctx context.Context, in *ScoreCardInfo) error
	SendSarifInfo(ctx context.Context, in *SarifInfo) error
	NotifyCVEsDataChanged(ctx context.Context, in *CVEIDs) error
}

// BuildInfo data object
type BuildInfo struct {
	ProductKey         string           `json:"productKey"`
	BuildNumber        string           `json:"buildNumber"`
	Hash               string           `json:"hash"`
	Date               string           `json:"date"`
	Integrity          string           `json:"integrity"`
	Context            json.RawMessage  `json:"context"`
	ClientID           string           `json:"clientId"`
	RequestID          int              `json:"requestId"`
	CVEScanID          *int             `json:"cveScanId,omitempty"`
	SBOMSynopsis       *domain.Synopsis `json:"sbomSynopsis,omitempty"`
	SignedFileID       int              `json:"signedFileId,omitempty"`    // if it was a signed SBOM, file ID of the original signed SBOM
	SignedRequestID    int              `json:"signedRequestId,omitempty"` // if it was a signed SBOM, request ID of the original signed SBOM
	VerificationStatus string           `json:"verifyStatus,omitempty"`    // unsigned / success / fail
	SignerID           string           `json:"signerID,omitempty"`        // if it was a signed SBOM, signer ID of the signed SBOM
	Info               string           `json:"info,omitempty"`            // additional info on verify errors
	DirBomFileSize     int              `json:"dirFileSize,omitempty"`
}

// CVEInfo data object
type CVEInfo struct {
	RequestID int `json:"requestId"`
	ScanID    int `json:"cveScanId"`
}

type CVEIDs struct {
	IDs []string `json:"ids"`
}

// ScoreCardInfo data object
type ScoreCardInfo struct {
	FileID    int `json:"fileId"`
	RequestID int `json:"requestId"`
}

func (b *BuildInfo) MarshalLogObject(enc zapcore.ObjectEncoder) error {
	enc.AddString("productKey", b.ProductKey)
	enc.AddString("buildNumber", b.BuildNumber)
	enc.AddString("hash", b.Hash)
	enc.AddString("date", b.Date)
	enc.AddString("integrity", b.Integrity)
	enc.AddString("clientId", b.ClientID)
	enc.AddInt("requestId", b.RequestID)
	enc.AddString("context", string(b.Context))
	if b.CVEScanID != nil {
		enc.AddInt("cveScanId", *b.CVEScanID)
	}
	return nil
}

// SarifInfo data object
type SarifInfo struct {
	ProductKey string          `json:"productKey"`
	FileID     int             `json:"fileId"`
	Hash       string          `json:"hash"`
	Date       string          `json:"date"`
	Context    json.RawMessage `json:"context"`
	ClientID   string          `json:"clientId"`
	RequestID  int             `json:"requestId"`
	Type       string          `json:"type"`
}

func (b *SarifInfo) MarshalLogObject(enc zapcore.ObjectEncoder) error {
	enc.AddString("productKey", b.ProductKey)
	enc.AddInt("fileId", b.FileID)
	enc.AddString("hash", b.Hash)
	enc.AddString("date", b.Date)
	enc.AddString("clientId", b.ClientID)
	enc.AddInt("requestId", b.RequestID)
	enc.AddString("context", string(b.Context))
	return nil
}
