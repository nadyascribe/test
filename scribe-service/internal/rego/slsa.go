//nolint:gofumpt
package rego

import (
	"context"
	"os"
	"regexp"

	"github.com/mitchellh/mapstructure"

	"github.com/scribe-security/scribe2/scribe-service/pkg/errors"
)

func InvokePolicy(
	ctx context.Context,
	provenanceFileURL string,
	protectedBranch string,
	token string,
	policyPath string,
	buildScriptPath string,
	repositoryName string,
	repositoryURL string,
	debug bool,
	outFile string,
) error {
	// policy input
	inputParams := make(map[string]interface{})
	obj := SlsaPolicyInput{
		Slsa: SlsaInput{
			Provenance:                    wrapLink(provenanceFileURL),
			ProtectedBranch:               protectedBranch,
			ReasonProvenanceAuthenticated: "a.sig",
			BuildScript:                   buildScriptPath,
			BuildService:                  "GitHub Actions",
			Repository:                    repositoryName,
			RepositoryURL:                 wrapLink(repositoryURL),
			AcceptRetainedIndefinitely:    true,
			Debug:                         debug,
		},
	}

	if err := mapstructure.Decode(obj, &inputParams); err != nil {
		return errors.Wrap(err)
	}

	inputParams["token"] = "token " + token

	result, err := ExecuteOpa(ctx, policyPath, "data.github.slsa.report", inputParams)
	if err != nil {
		return errors.Wrap(err)
	}

	if result == nil {
		return errors.New("policy.Execute on org policy returned empty response")
	}

	f, err := os.Create(outFile)

	if err != nil {
		return errors.Wrap(err)
	}

	defer f.Close()

	if _, err := f.Write(result); err != nil {
		return errors.Wrap(err)
	}

	return nil
}

func wrapLink(s string) string {
	reLinks := regexp.MustCompile(`(https?://\S+)`)
	return reLinks.ReplaceAllString(s, `<a href="$1" target="_blank">here</a>`)
}

//nolint:lll
type SlsaInput struct {
	Provenance                    string `yaml:"provenance,omitempty" json:"provenance,omitempty" mapstructure:"provenance,omitempty"`
	ProtectedBranch               string `yaml:"protected_branch,omitempty" json:"protected_branch,omitempty" mapstructure:"protected_branch,omitempty"`
	ReasonProvenanceAuthenticated string `yaml:"reason_provenance_authenticated,omitempty" json:"reason_provenance_authenticated,omitempty" mapstructure:"reason_provenance_authenticated,omitempty"`
	BuildScript                   string `yaml:"build_script,omitempty" json:"build_script,omitempty" mapstructure:"build_script,omitempty"`
	BuildService                  string `yaml:"build_service,omitempty" json:"build_service,omitempty" mapstructure:"build_service,omitempty"`
	Repository                    string `yaml:"repository,omitempty" json:"repository,omitempty" mapstructure:"repository,omitempty"`
	RepositoryURL                 string `yaml:"repository_url,omitempty" json:"repository_url,omitempty" mapstructure:"repository_url,omitempty"`
	AcceptRetainedIndefinitely    bool   `yaml:"accept_retained_indefinitely,omitempty" json:"accept_retained_indefinitely,omitempty" mapstructure:"accept_retained_indefinitely,omitempty"`
	Debug                         bool   `yaml:"debug" json:"debug" mapstructure:"debug"`
}

type SlsaPolicyInput struct {
	Slsa  SlsaInput `yaml:"slsa,omitempty" json:"slsa,omitempty" mapstructure:"slsa,omitempty"`
	Token string    `yaml:"token,omitempty" json:"token,omitempty" mapstructure:"token,omitempty"`
}
