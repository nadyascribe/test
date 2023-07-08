package config

import (
	"context"
	"fmt"
	"os"
	"path"
	"path/filepath"
	"reflect"

	"github.com/kelseyhightower/envconfig"
	"github.com/palantir/go-githubapp/githubapp"
	"sigs.k8s.io/json"

	"github.com/scribe-security/scribe2/scribe-service/pkg/errors"
	"github.com/scribe-security/scribe2/scribe-service/pkg/helpers"
	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

type Config struct {
	Environment string `envconfig:"SCRIBE_ENVIRONMENT" json:"environment,omitempty"`
	Namespace   string `envconfig:"NAMESPACE" json:"namespace,omitempty"`

	FileTransfers FileTransfers `envconfig:"FILE_TRANSFERS" json:"filetransfers"`
	Postgres      Postgres      `envconfig:"POSTGRES" json:"postgres"`
	Auth0         Auth0         `envconfig:"AUTH0" json:"auth0"`
	// Github there is no `envconfig` tag because it is set by githubapps's library, method `SetValuesFromEnv`
	Github  githubapp.Config `json:"github"`
	Airflow Airflow          `envconfig:"AIRFLOW" json:"airflow"`
}

var errNoEnv = errors.New("no env tag")

func (cfg *Config) getEnvTag() (string, error) {
	field, ok := reflect.TypeOf(*cfg).FieldByName("Environment") // not json:name

	if !ok {
		return "", errors.Errorf("cannot find a tag for environment")
	}

	envNameTag := field.Tag.Get("envconfig")
	if envNameTag == "" {
		return "", errors.Errorf("cannot find env name tag")
	}
	envName := os.Getenv(envNameTag)
	if envName == "" {
		return "", errors.Wrap(errNoEnv, "cannot find env name var")
	}
	return envName, nil
}

type Airflow struct {
	APIUrl   string `envconfig:"API_URL" json:"api_url,omitempty"`
	Login    string `envconfig:"LOGIN" json:"login,omitempty"`
	Password string `envconfig:"PASSWORD" json:"password,omitempty"`
}

type Postgres struct {
	Host     string `envconfig:"HOST" json:"host,omitempty"`
	Port     int    `envconfig:"PORT" json:"port,omitempty"`
	User     string `envconfig:"USER" json:"user,omitempty"`
	Password string `envconfig:"PASSWORD" json:"password,omitempty"`
	DB       string `envconfig:"DB" json:"db,omitempty"`
}

func (cfg Postgres) String() string {
	return fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable", cfg.Host, cfg.Port, cfg.User, cfg.Password, cfg.DB)
}

type Auth0 struct {
	Audiences Auth0Audiences `envconfig:"AUDIENCES" json:"audiences"`
	Domain    string         `envconfig:"DOMAIN" json:"domain,omitempty"`
}

func (a Auth0) GetLoginURL() string {
	return fmt.Sprintf("https://%s", a.Domain)
}

type Auth0Audiences struct {
	ScribeHub     string `envconfig:"SCRIBE_HUB" json:"scribe_hub,omitempty"`
	ScribeBackend string `envconfig:"SCRIBE_BACKEND" json:"scribe_backend,omitempty"`
}

type FileTransfers struct {
	BucketName    string `envconfig:"BUCKET_NAME" json:"bucket_name,omitempty"`
	MixpanelToken string `envconfig:"MIXPANEL_TOKEN" json:"mixpanel_token,omitempty"`
	DefaultRegion string `envconfig:"DEFAULT_REGION" default:"us-west-2" json:"default_region,omitempty"`
}

func New() (*Config, error) {
	cfg := Config{}

	envName, errEnv := cfg.getEnvTag()
	switch {
	case errors.Is(errEnv, errNoEnv):
		log.L(context.Background()).Warn("no env tag, using default")
		envName = "default"
	case errEnv != nil:
		return nil, errEnv
	}

	configsPath := helpers.GetEnv("SCRIBE_CONFIG_PATH", "./configs")
	configFilePath, err := filepath.Abs(path.Join(configsPath, fmt.Sprintf("%s.json", envName)))
	if err != nil {
		return nil, err
	}

	bytes, err := os.ReadFile(configFilePath)
	if err != nil {
		return nil, errors.Wrapf(err, "failed reading server config file")
	}
	if _, err := json.UnmarshalStrict(bytes, &cfg); err != nil {
		return nil, errors.Wrap(err, "failed parsing configuration file")
	}

	cfg.Github.SetValuesFromEnv("")
	if err := envconfig.Process("", &cfg); err != nil {
		return nil, err
	}

	if errEnv == nil && envName != cfg.Environment {
		return nil, errors.New("envs not equal")
	}

	if cfg.Airflow.APIUrl == "" {
		cfg.Airflow.APIUrl = fmt.Sprintf("http://webserver-airflow.%s:8080/api/v1", cfg.Namespace)
	}

	return &cfg, nil
}
