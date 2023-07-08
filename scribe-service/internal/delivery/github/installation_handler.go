package github

import (
	"context"
	"encoding/json"

	"github.com/google/go-github/v50/github"
	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/pkg/errors"
	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

func (h *Handler) handleInstallation(ctx context.Context, data []byte) error {
	logger := log.L(ctx)
	var event github.InstallationEvent
	if err := json.Unmarshal(data, &event); err != nil {
		return errors.Wrap(err, "failed to parse worflow run event payload")
	}

	logger.Logger().With(zap.String("action", event.GetAction()),
		zap.Strings("repositories", func() []string {
			repos := make([]string, 0, len(event.Repositories))
			for _, r := range event.Repositories {
				repos = append(repos, r.GetHTMLURL())
			}
			return repos
		}()))

	switch act := event.GetAction(); act {
	case "created":
		logger.Info("installation received")
	case "deleted", "suspend":
		return errors.Wrap(h.service.DisableGithubInstallation(ctx, event.Installation.GetID()))
	case "unsuspend":
		return errors.Wrap(h.service.EnableGithubInstallation(ctx, event.Installation.GetID()))
	case "new_permissions_accepted":
		logger.Info("new permissions accepted")
	default:
		logger.Warn("unsupported event type", zap.String("event", act))
	}

	return nil
}
