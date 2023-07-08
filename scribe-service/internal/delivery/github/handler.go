package github

import (
	"context"

	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/internal/domain"
	"github.com/scribe-security/scribe2/scribe-service/pkg/errors"
	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

type CreateHandlerParameters struct {
	Service domain.EvidenceStoreService
}

type Handler struct {
	service domain.EvidenceStoreService
}

func New(params CreateHandlerParameters) *Handler {
	return &Handler{service: params.Service}
}

func (h *Handler) Handles() []string {
	return []string{"workflow_run", "installation"}
}

func (h *Handler) Handle(ctx context.Context, eventType, deliveryID string, payload []byte) error {
	logger := log.L(ctx).Logger().With(zap.String("deliveryID", deliveryID))
	logger.Debug(
		"handling event",
		zap.ByteString("event", payload),
	)

	var err error
	switch eventType {
	case "workflow_run":
		err = h.handleWorkflowRun(ctx, payload)
	case "installation":
		err = h.handleInstallation(ctx, payload)
	default:
		err = errors.Errorf("unsupported event type %s", eventType)
	}

	if err != nil {
		logger.Error("error during event handling", zap.Error(err))
	}
	return errors.Wrap(err)
}
