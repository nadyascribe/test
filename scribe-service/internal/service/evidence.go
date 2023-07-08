package service

import (
	"context"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/url"
	"path/filepath"
	"strings"
	"time"
	"unicode"

	"github.com/dukex/mixpanel"
	"github.com/golang-jwt/jwt"
	"github.com/google/uuid"
	"github.com/scribe-security/cocosign/storer/evidence"
	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/internal/domain"
	"github.com/scribe-security/scribe2/scribe-service/pkg/errors"
	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

// CreateEvidence invokes cloud storage presign URL call and returns this URL.
// If the user input flags in valint are invalid, returns error domain.ErrInvalidPipelineParams.
//
//nolint:funlen,gocyclo
func (s *service) CreateEvidence(
	ctx context.Context, in *domain.UploadEvidenceFileTransfer,
) (*domain.CreateEvidenceOutputBody, error) {
	if in == nil {
		return nil, errors.New("input is nil")
	}

	if in.ContextData == nil {
		log.L(ctx).Error("the ContextData received was nil", zap.String("key", in.Key))
		return nil, errors.New("the ContextData received was nil")
	}

	attrs := domain.FileTransferAttributes{
		Bucket:       s.fst.GetBucketName(),
		CloudStorage: s.fst.GetStorageType(),
	}

	// add the user ID to the key to avoid collisions
	keyToStore := filepath.Join(
		hex.EncodeToString([]byte(fmt.Sprintf("%d", in.TeamID))),
		in.Key,
	)

	presignedURL, err := s.GetPresignedURLandAttrs(ctx, keyToStore)
	if err != nil {
		log.L(ctx).Error("get presigned URL and attributes", zap.Error(err))
		return nil, err
	}

	contextData := make(map[string]interface{})

	if err = json.Unmarshal(in.ContextData, &contextData); err != nil {
		log.L(ctx).Error("unmarshal metadata", zap.Error(err), zap.Any("in.ContextData", string(in.ContextData)))
		return nil, err
	}

	// check if pipeline is exists, if not - create it
	p := getPipelineRunParams(contextData, in.TeamID)

	if p.ProductKey == "" {
		log.L(ctx).Error("invalid pipeline params - product key is empty",
			zap.String("pipelineName", p.PipelineName),
			zap.String("pipelineRun", p.PipelineRun),
			zap.String("version", p.Version))
		return nil, domain.ErrInvalidProductKey
	}

	if p.PipelineName == "" || p.PipelineRun == "" {
		log.L(ctx).Error("invalid pipeline params",
			zap.String("productKey", p.ProductKey),
			zap.String("pipelineName", p.PipelineName),
			zap.String("pipelineRun", p.PipelineRun))
		return nil, domain.ErrInvalidPipelineParams
	}

	pipeline, err := s.r.GetPipelineRun(ctx, &domain.GetPipelineRunInput{
		ProductKey:   p.ProductKey,
		PipelineName: p.PipelineName,
		PipelineRun:  p.PipelineRun,
		TeamID:       in.TeamID,
	})
	if pipeline != nil && err == nil {
		log.L(ctx).Info("pipeline exists, skipping creation...", zap.String("productKey", p.ProductKey))
	}
	if err == sql.ErrNoRows {
		log.L(ctx).Info("no existing pipeline, creating new pipeline...", zap.String("productKey", p.ProductKey))
		pipeline, err = s.r.CreatePipelineRun(ctx, &domain.PipelineRunObj{
			ProductKey:   p.ProductKey,
			PipelineName: p.PipelineName,
			PipelineRun:  p.PipelineRun,
			Context:      &in.ContextData,
			Version:      p.Version,
			Team:         in.TeamID,
		})
		if err != nil {
			log.L(ctx).Error("create pipeline run", zap.Error(err))
		}
	} else if err != nil {
		log.L(ctx).Error("get pipeline, DB error", zap.Error(err))
	}

	// TODO: refactor the context parsing later
	metadata := json.RawMessage(`{}`)
	if in.ContextData != nil {
		metadata = in.ContextData
	}

	var ctxData evidence.AllContext
	if err := json.Unmarshal(metadata, &ctxData); err != nil {
		log.L(ctx).Error("unmarshal context data", zap.Error(err))
		return nil, err
	}

	targetType := ctxData.TargetHeader.Type
	targetName := ctxData.InputName()

	// according to tocket SH-2001
	if targetType == "generic" {
		targetType = "other"
	}

	fileID, err := s.r.CreateEvidence(ctx, &domain.PGCreateEvidenceInput{
		Key: fmt.Sprintf("%s://%s/%s",
			attrs.CloudStorage,
			attrs.Bucket,
			keyToStore,
		),
		TeamID:      in.TeamID,
		ContentType: in.ContentType,
		ContextType: in.ContextType,
		ContextData: in.ContextData,
		PipelineRun: pipeline.ID,
		TargetName:  targetName,
		TargetType:  targetType,
	})
	if err != nil {
		log.L(ctx).Error("create file transfer with metadata", zap.Error(err))
		return nil, err
	}

	return &domain.CreateEvidenceOutputBody{
		FileID:       fileID,
		PresignedURL: presignedURL,
	}, nil
}

func (s *service) GetLastPipelineRunForRepos(ctx context.Context, repos ...string) (*domain.PipelineRunObj, error) {
	pipeline, err := s.r.GetPipelineRunByGitURLs(ctx, repos...)
	switch {
	case errors.Is(err, sql.ErrNoRows):
		return nil, nil
	case err != nil:
		log.L(ctx).Error("get pipeline, DB error", zap.Error(err))
		return nil, errors.Wrap(err)
	default:
		return pipeline, nil
	}
}

// get presigned URL from cloud storage and the s3 attributes
func (s *service) GetPresignedURLandAttrs(ctx context.Context, key string) (
	presignedURL string, err error,
) {
	l := log.L(ctx).Logger().With(
		zap.String("bucket", s.fst.GetBucketName()), zap.String("key", key))

	// check if the key already exists
	_, err = s.r.GetEvidenceByKey(ctx, key)
	if err != nil && err != domain.ErrSQLEmptyRecord {
		l.Error("db error to get evidence object by key", zap.Error(err))
		return "", err
	}

	presignedURL, err = s.fst.GetUploadURL(ctx, key)
	if err != nil {
		return "", err
	}

	return presignedURL, nil
}

func getS3keyFromDBkey(dbKey string) (string, error) {
	keyURL, err := url.Parse(dbKey)
	if err != nil {
		return "", err
	}

	return strings.TrimLeft(keyURL.Path, "/"), nil
}

// FinishEvidenceFileTransfer by FileID and update status in the database.
func (s *service) FinishEvidenceFileTransfer(
	ctx context.Context,
	in *domain.FinishUploadEvidenceWithTeamID,
) error {
	l := log.L(ctx).Logger().With(zap.Int("fileID", in.FileID))
	var runtimeError error
	if in.Error != nil && *in.Error != "" {
		l.Warn("file transfer finished with fail", zap.String("error", *in.Error))
		runtimeError = fmt.Errorf("file transfer finished with fail: %s", *in.Error)
	}

	var attest *domain.Attestation
	var err error
	contextData := make(map[string]interface{})
	var marshaledContextData []byte
	// only if file was uploaded successfully, we try to get the file metadata
	// and add the file size to it
	if in.Error == nil || *in.Error == "" {
		attest, err = s.r.GetEvidenceByID(ctx, in.FileID)
		if err != nil {
			l.Error("get file transfer", zap.Error(err))
			return err
		}

		S3key, err := getS3keyFromDBkey(*attest.Key)
		if err != nil {
			l.Error("get S3 key from DB key", zap.Error(err))
			return err
		}

		fileSize, err := s.fst.GetFileSize(ctx, S3key)
		if err != nil {
			l.Error("get file size", zap.Error(err))
			return err
		}

		if err = json.Unmarshal(attest.Context, &contextData); err != nil {
			l.Error("unmarshal metadata", zap.Error(err), zap.Any("attest.Context", string(attest.Context)))
			return err
		}

		// this will stop analyze from continuing and failing later without clear reason
		if contextData == nil {
			return errors.New("uploaded contextData is empty")
		}

		contextData["file_size"] = fileSize
		if marshaledContextData, err = json.Marshal(contextData); err != nil {
			l.Error("marshal metadata", zap.Any("attest.Context", string(attest.Context)))
			return err
		}

		err = s.r.UpdateContext(ctx, in.FileID, (*json.RawMessage)(&marshaledContextData))
		if err != nil {
			l.Error("update context", zap.Error(err))
			return err
		}
	}

	if err := s.r.FinishUploadEvidence(ctx, &domain.FinishUploadEvidenceWithTeamID{
		FileID: in.FileID,
		Error:  in.Error,
		TeamID: in.TeamID,
	}); err != nil {
		l.Error("update file transfer status", zap.Error(err))
		return err
	}

	if runtimeError != nil {
		l.Error(
			"error finishing file transfer",
			zap.Error(runtimeError),
		)
		return runtimeError
	}

	if err := s.CreateProduct(ctx, contextData, in.TeamID); err != nil {
		l.Error("create product failed", zap.Error(err))
		return err
	}

	return nil
}

// CreateProduct creates a product in the database
func (s *service) CreateProduct(
	ctx context.Context,
	contextData map[string]interface{},
	teamID int64,
) error {
	// get user product key from contextData name
	validatedProductKey := createProductKey(contextData)
	if validatedProductKey == "" {
		log.L(ctx).Error("validated product key is empty, can't create product")
		return fmt.Errorf("validated product key is empty, can't create product")
	}

	// get product from DB by key
	product, err := s.r.GetProduct(ctx, validatedProductKey, teamID)
	if err == domain.ErrSQLEmptyRecord {
		log.L(ctx).Info("product doesn't exist, creating new product")
	} else if err != nil {
		log.L(ctx).Error("db error to get product by key", zap.Error(err))
		return err
	}

	if product != nil {
		log.L(ctx).Info("product already exists, skipping creation")
		return nil
	}

	// create product
	product = &domain.Product{
		Name:           validatedProductKey,
		TeamID:         teamID,
		Key:            generateUUIDfromUserKey(validatedProductKey, teamID),
		UserDefinedKey: validatedProductKey,
	}

	p, err := s.r.CreateProduct(ctx, product)
	if err != nil {
		log.L(ctx).Error("db error to create product", zap.Error(err))
		return err
	}
	if p != nil {
		log.L(ctx).Info("product created successfully", zap.Int64("productID", p.ID),
			zap.String("userProductKey", p.UserDefinedKey))
	}

	return nil
}

// generate UUID from the userProductKey
func generateUUIDfromUserKey(userProductKey string, teamID int64) string {
	uniqueKey := fmt.Sprintf("%d%s", teamID, userProductKey)
	return uuid.NewSHA1(uuid.NameSpaceOID, []byte(uniqueKey)).String()
}

// create a product key from the contextData and validate it
// if couldn't find a relevant value in the contextData, return empty string
func createProductKey(contextData map[string]interface{}) string {
	contextKeysToCheck := []string{"name", "git_url", "input_name", "target_git_url", "dir_path", "file_path"}
	for _, key := range contextKeysToCheck {
		if value, ok := contextData[key].(string); ok {
			if value != "" && validateInput(value) != "" {
				return validateInput(value)
			}
		}
	}
	return ""
}

var allowedChars = map[rune]bool{
	'.': true,
	'%': true,
	'-': true,
	'_': true,
	'@': true,
	'~': true,
	'!': true,
	'=': true,
	'[': true,
	']': true,
	'&': true,
	'#': true,
	'+': true,
	',': true,
	' ': true,
}

func validateInput(input string) string {
	trimmedInput := strings.TrimRight(input, " ")

	var validatedInput strings.Builder
	for _, r := range trimmedInput {
		if unicode.IsLetter(r) || unicode.IsNumber(r) || allowedChars[r] {
			validatedInput.WriteRune(r)
		} else {
			validatedInput.WriteString(fmt.Sprintf("\\u%04X", r))
		}
	}

	return validatedInput.String()
}

type PipelineParams struct {
	ProductKey   string
	PipelineName string
	PipelineRun  string
	Version      string
}

//nolint:gocritic
func getPipelineRunParams(contextData map[string]interface{}, teamID int64) PipelineParams {
	var params PipelineParams

	// design: productKey = BaseHeader.NameField
	validatedName := createProductKey(contextData)
	if validatedName != "" {
		params.ProductKey = generateUUIDfromUserKey(validatedName, teamID)
	}

	// design: pipelineName = BaseHeader.PipelineName or BasePipelineHeader.workflow or ContextType
	if contextData["pipeline_name"] != nil {
		params.PipelineName = validateInput(contextData["pipeline_name"].(string))
	}
	if params.PipelineName == "" && contextData["workflow"] != nil {
		params.PipelineName = validateInput(contextData["workflow"].(string))
	}
	if params.PipelineName == "" && contextData["context_type"] != nil {
		params.PipelineName = validateInput(contextData["context_type"].(string))
	}

	// design: pipelineRun = BasePipelineHeader.RunID or ContextType + round_down(now(), 10mins)
	if contextData["run_id"] != nil {
		params.PipelineRun = validateInput(contextData["run_id"].(string))
	} else {
		t := time.Now()
		rounded := t.Add(-time.Duration(t.Minute()%10) * time.Minute).Truncate(10 * time.Minute) //nolint:gomnd
		if contextData["context_type"] != nil {
			params.PipelineRun = fmt.Sprintf("%s %s", validateInput(contextData["context_type"].(string)), rounded.String())
		} else {
			params.PipelineRun = rounded.String()
		}
	}

	// design: version = “product_version” (valint flag -V) or “sbomversion” or timestamp (from context)
	if contextData["product_version"] != nil {
		params.Version = validateInput(contextData["product_version"].(string))
	}
	if params.Version == "" && contextData["sbomversion"] != nil {
		params.Version = validateInput(contextData["sbomversion"].(string))
	}
	if params.Version == "" && contextData["timestamp"] != nil {
		params.Version = validateInput(contextData["timestamp"].(string))
	}

	return params
}

// DeleteEvidence by key pattern or one file by fileID.
// returns domain.ErrFileTransferAccessDenied if file belongs to another user
func (s *service) DeleteEvidence(
	ctx context.Context, in *domain.DeleteEvidenceServiceInput,
) error {
	emptyKey := ""

	return s.r.DeleteEvidence(ctx, &domain.DeleteEvidenceRepoInput{
		FileID: &in.FileID,
		Key:    &emptyKey,
		TeamID: in.TeamID,
	})
}

// GetEvidenceDownload returns presigned URL for download by fileID.
func (s *service) GetEvidenceDownload(
	ctx context.Context, in *domain.GetEvidenceDownloadInput,
) (*domain.GetEvidenceDownloadOutputBody, error) {
	l := log.L(ctx).Logger().With(zap.Int("file_id", in.FileID))

	record, err := s.r.GetEvidenceByID(ctx, in.FileID)
	if err != nil {
		l.Error("get evidence object by file_id", zap.Error(err))
		return nil, err
	}
	if record == nil {
		l.Error("evidence object not exists")
		return nil, fmt.Errorf("does not exist")
	}
	if record.TeamID == nil {
		l.Error("evidence object has no teamId")
		return nil, fmt.Errorf("evidence teamId does not exist")
	}

	if *record.TeamID != in.TeamID {
		l.Error(
			"file access denied",
			zap.Int64("in.TeamID", in.TeamID),
			zap.Int64("record.TeamId", *record.TeamID),
		)
		return nil, domain.ErrFileTransferAccessDenied
	}

	if record.Key == nil {
		l.Error("evidence object has no key")
		return nil, fmt.Errorf("evidence key does not exist")
	}

	S3key, err := getS3keyFromDBkey(*record.Key)
	if err != nil {
		l.Error("get S3 key from DB key", zap.Error(err))
		return nil, err
	}

	presignedURL, err := s.fst.GetDownloadURL(ctx, S3key)
	if err != nil {
		return nil, err
	}

	return &domain.GetEvidenceDownloadOutputBody{PresignedURL: presignedURL}, nil
}

// SendMixpanelEvent sends an event with a given name and properties to mix panel,
// with the user email as the mixpanel distinctID.
// The email is extracted by getting the projectID, querying the projects table for the auth0 OwnerID
// and getting the user info from auth0.
func (s *service) SendMixpanelEvent(
	ctx context.Context,
	in *domain.SendMixpanelEventInputs,
) error {
	if s.cfg.MixpanelToken == "" {
		return fmt.Errorf("couldn't get mixpanel token")
	}

	if in.TokenType == "" {
		return fmt.Errorf("token type field is empty")
	}

	if in.UserToken == "" {
		return fmt.Errorf("token field is empty")
	}

	distinctID, addProperties := s.mixpanelInputs(ctx, in.Properties, in.TokenType, &in.UserToken)
	in.Properties = append(in.Properties, addProperties...)

	client := mixpanel.New(s.cfg.MixpanelToken, "")

	timestamp := time.Now()

	prpt := make(map[string]interface{})
	for i := range in.Properties {
		prpt[in.Properties[i].Key] = in.Properties[i].Value
	}

	event := mixpanel.Event{
		IP:         in.IP,
		Timestamp:  &timestamp,
		Properties: prpt,
	}

	err := client.Track(distinctID, in.EventName, &event)
	if err != nil {
		log.L(ctx).Error("mixpanel sbom event failed", zap.Error(err))
		return err
	}

	log.L(ctx).Info("mixpanel event sent", zap.String("event_name", in.EventName), zap.Any("properties", prpt))

	return nil
}

type FrontendClaims struct {
	jwt.StandardClaims
	UserID string `json:"azp,omitempty"`
	Email  string `json:"email,omitempty"`
}

type GensbomClaims struct {
	jwt.StandardClaims
	UserID           string `json:"azp,omitempty"`
	TeamName         string `json:"https://scribe-security/team-name,omitempty"`
	TeamCreatorEmail string `json:"https://scribe-security/team-creator-email,omitempty"`
}

func (s *service) mixpanelInputs(
	ctx context.Context, properties []domain.MixapanelProperties, tokenType domain.MixapanelTokenType, token *string) (
	distinctID string, _ []domain.MixapanelProperties,
) {
	parser := jwt.Parser{
		SkipClaimsValidation: true,
	}

	switch tokenType {
	case domain.MixpanelTokenGensbom:
		// the token was already verified by fiber in the handler, no need to verify again
		myClaims := GensbomClaims{}
		_, _, err := parser.ParseUnverified(*token, &myClaims)
		if err != nil {
			log.L(ctx).Error("ParseUnverified token parse failed", zap.Error(err))
		}

		properties = append(properties, []domain.MixapanelProperties{
			{
				Key:   "Team Name",
				Value: myClaims.TeamName,
			},
			{
				Key:   "Team Creator Email",
				Value: myClaims.TeamCreatorEmail,
			},
			{
				Key:   "Scribe Environment",
				Value: s.env,
			},
		}...)

		distinctID = myClaims.TeamCreatorEmail
	case domain.MixpanelTokenFrontend:
		// the token was already verified by fiber in the handler, no need to verify again
		myClaims := FrontendClaims{}
		_, _, err := parser.ParseUnverified(*token, &myClaims)
		if err != nil {
			log.L(ctx).Error("ParseUnverified token parse failed", zap.Error(err))
		}

		properties = append(properties, []domain.MixapanelProperties{
			{
				Key:   "Scribe Environment",
				Value: s.env,
			},
		}...)

		distinctID = myClaims.Email
	}

	return distinctID, properties
}

// ListReports reuturs a list of process states for given query.
func (s *service) ListReports(
	ctx context.Context, queryJSON *json.RawMessage, userID int64,
) ([]domain.Attestation, error) {
	return s.r.ListEvidence(ctx, queryJSON, userID)
}
