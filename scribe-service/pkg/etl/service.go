package etl

import (
	"bytes"
	"context"
	"io"
	"net/http"
	"net/url"

	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/pkg/config"
	"github.com/scribe-security/scribe2/scribe-service/pkg/errors"
	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

type service struct {
	http   *http.Client
	config config.Airflow
}

func New(cfg config.Airflow) Airflow {
	return &service{
		http:   http.DefaultClient,
		config: cfg,
	}
}

func (s *service) TriggerETL(ctx context.Context, etlName string, payload []byte) error {
	l := log.L(ctx).Logger().With(zap.String("etl_name", etlName), zap.String("api_url", s.config.APIUrl))

	l.Debug("triggering etl", zap.ByteString("payload", payload))
	urlPath, err := url.JoinPath(s.config.APIUrl, "dags", etlName, "dagRuns")
	if err != nil {
		return errors.Wrap(err, "failed to join url path")
	}

	req, err := http.NewRequestWithContext(ctx, "POST",
		urlPath,
		bytes.NewBuffer(payload),
	)
	if err != nil {
		return errors.Wrap(err, "failed to create request")
	}

	req.Header.Set("Content-Type", "application/json")
	req.SetBasicAuth(s.config.Login, s.config.Password)

	resp, err := s.http.Do(req)
	if err != nil {
		return errors.Wrap(err)
	}

	defer resp.Body.Close()
	respBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return errors.Wrap(err, "failed to read response body")
	}

	l.Debug(
		"triggered etl",
		zap.Int("status_code", resp.StatusCode),
		zap.ByteString("response", respBytes))

	return nil
}
