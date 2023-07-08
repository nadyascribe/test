package httpclient

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"

	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
	"github.com/scribe-security/scribe2/scribe-service/pkg/schub"
)

// Client of HTTP API of the Scribe Hub
type Client struct {
	http *http.Client

	baseURL  string
	user     string
	password string
}

// New instance contstuctor of the client
func New(baseURL, user, password string) *Client {
	return &Client{
		http:     http.DefaultClient,
		baseURL:  strings.TrimRight(baseURL, "/"),
		user:     user,
		password: password,
	}
}

// SendBuildInfo notifies Scribe Hub about build create/update
func (c *Client) SendBuildInfo(ctx context.Context, in *schub.BuildInfo) error {
	l := log.L(ctx).Logger().With(
		zap.String("type", "build"),
		zap.Object("build_info", in),
		zap.Int("request_id", in.RequestID))
	return c.doRequest(ctx, l, "/internal/builds", in)
}

// SendCVEInfo notifies Scribe Hub about new CVE report
func (c *Client) SendCVEInfo(ctx context.Context, in *schub.CVEInfo) error {
	l := log.L(ctx).Logger().With(
		zap.String("type", "cve"),
		zap.Int("scan_id", in.ScanID),
		zap.Int("request_id", in.RequestID))
	return c.doRequest(ctx, l, "/internal/cve-scans", in)
}

func (c *Client) NotifyCVEsDataChanged(ctx context.Context, in *schub.CVEIDs) error {
	l := log.L(ctx).Logger().With(zap.String("type", "cve-data-changed"))
	return c.doRequest(ctx, l, "/internal/cves", in)
}

// SendSarifInfo notifies Scribe Hub about new sarif report
func (c *Client) SendSarifInfo(ctx context.Context, in *schub.SarifInfo) error {
	l := log.L(ctx).Logger().With(
		zap.Int("file_id", in.FileID),
		zap.String("type", in.Type),
		zap.Int("request_id", in.RequestID))
	return c.doRequest(ctx, l, "/internal/compliance", in)
}

// SendScanInfo notifies Scribe Hub about build score card
func (c *Client) SendScoreCardInfo(ctx context.Context, in *schub.ScoreCardInfo) error {
	l := log.L(ctx).Logger().With(
		zap.Int("file_id", in.FileID),
		zap.Int("request_id", in.RequestID))
	return c.doRequest(ctx, l, "/internal/scorecard", in)
}

// doRequest performs HTTP request to Scribe Hub
func (c *Client) doRequest(ctx context.Context, l *zap.Logger, u string, in interface{}) error {
	u = c.baseURL + u

	data, err := json.Marshal(in)
	l.Debug("notify scribehub", zap.ByteString("data", data), zap.String("url", u))
	if err != nil {
		l.Error("marshal send object", zap.Error(err))
		return err
	}

	request, err := http.NewRequestWithContext(ctx, http.MethodPost, u, bytes.NewReader(data))
	if err != nil {
		l.Error("create new request object", zap.Error(err))
		return err
	}
	request.SetBasicAuth(c.user, c.password)
	request.Header.Set("Content-Type", "application/json")

	response, err := c.http.Do(request)
	if err != nil {
		l.Error("do request to scribe hub", zap.Error(err))
		return err
	}
	data, err = io.ReadAll(response.Body)
	if err != nil {
		l.Error("read response body", zap.Error(err))
	}
	defer response.Body.Close()

	if response.StatusCode < http.StatusOK || response.StatusCode >= http.StatusMultipleChoices {
		l.Error("wrong status code",
			zap.Int("status", response.StatusCode), zap.String("body", string(data)))
		return fmt.Errorf("wrong status code from scribe hub: %d", response.StatusCode)
	}
	return nil
}
