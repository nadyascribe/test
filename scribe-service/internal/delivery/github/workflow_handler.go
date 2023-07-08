package github

import (
	"context"
	"encoding/json"

	"github.com/google/go-github/v50/github"
	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/pkg/errors"
	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

func (h *Handler) handleWorkflowRun(ctx context.Context, data []byte) error {
	logger := log.L(ctx)
	var event github.WorkflowRunEvent
	if err := json.Unmarshal(data, &event); err != nil {
		return errors.Wrap(err, "failed to parse worflow run event payload")
	}

	if *event.Action != "completed" {
		logger.Debug("skip uncompleted run")
		return nil
	}

	pipeline, err := h.service.GetLastPipelineRunForRepos(ctx,
		event.Repo.GetHTMLURL(),
		event.Repo.GetCloneURL(),
		event.Repo.GetSSHURL(),
	)
	switch {
	case err != nil:
		logger.Error("failed to get pipeline run", zap.Error(err))
		return errors.Wrap(err)
	case pipeline == nil:
		logger.Debug("no pipeline run found, skip etl trigger")
		return nil
	}

	// Using a pointer to triggerSarifReportsPayload is a way to avoid copying a large struct when calling it's methods,
	// while still using value receivers for those methods.
	payload := &triggerSarifReportsPayload{
		InstallationID:  event.Installation.GetID(),
		WorkflowRunID:   event.GetWorkflowRun().GetID(),
		RepositoryID:    event.Repo.GetID(),
		RepositoryURL:   event.Repo.GetHTMLURL(),
		PipelineRunID:   pipeline.ID,
		BuildScriptPath: event.Workflow.GetPath(),
		DefaultBranch:   event.Repo.GetDefaultBranch(),
		RepoFullName:    event.Repo.GetFullName(),
		Debug:           false,
	}

	if err := h.service.TriggerETL(ctx, payload); err != nil {
		return errors.Wrap(err, "failed to trigger etl")
	}
	return nil
}

type triggerSarifReportsPayload struct {
	InstallationID  int64  `json:"installation_id"`
	RepositoryID    int64  `json:"repository_id"`
	RepositoryURL   string `json:"repository_url"`
	WorkflowRunID   int64  `json:"workflow_run_id"`
	PipelineRunID   int64  `json:"pipeline_run_id"`
	BuildScriptPath string `json:"build_script_path"`
	DefaultBranch   string `json:"default_branch"`
	RepoFullName    string `json:"repo_full_name"`
	Debug           bool   `json:"debug"`
}

//nolint:gocritic
func (e triggerSarifReportsPayload) TriggerETLPayload() {}

//nolint:gocritic
func (e triggerSarifReportsPayload) EtlName() string {
	return "github-app-attestations"
}

//nolint:gocritic
func (e triggerSarifReportsPayload) GetPayload() (map[string]interface{}, error) {
	b, err := json.Marshal(&e)
	if err != nil {
		return nil, errors.Wrap(err)
	}
	var m map[string]interface{}
	err = json.Unmarshal(b, &m)
	return m, err
}
