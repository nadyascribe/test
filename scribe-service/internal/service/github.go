package service

import (
	"context"

	"github.com/scribe-security/scribe2/scribe-service/pkg/errors"
)

func (s *service) DisableGithubInstallation(ctx context.Context, installationID int64) error {
	return errors.Wrap(s.r.DisableGithubInstallation(ctx, installationID))
}

func (s *service) EnableGithubInstallation(ctx context.Context, installationID int64) error {
	return errors.Wrap(s.r.EnableGithubInstallation(ctx, installationID))
}
