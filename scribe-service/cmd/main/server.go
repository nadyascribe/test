// Package classification Scribe API.
//     Schemes: http, https
//     Host: localhost:4000
//     BasePath: /
//     Version: 0.0.1
//     License: MIT http://opensource.org/licenses/MIT
//     Contact: Ori Avraham <ori@scribesecurity.com>
//     Consumes:
//     - application/json
//     Produces:
//     - application/json
//     Security:
//     - JWT:
//     SecurityDefinitions:
//     JWT:
//          type: apiKey
//          name: Authorization
//          in: header
// swagger:meta
package main

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/aws/retry"
	awsc "github.com/aws/aws-sdk-go-v2/config"
	"github.com/gofiber/adaptor/v2"
	"github.com/gofiber/fiber/v2"
	"github.com/jmoiron/sqlx"
	"github.com/palantir/go-githubapp/githubapp"
	"github.com/spf13/cobra"
	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/internal/delivery/github"
	delivery "github.com/scribe-security/scribe2/scribe-service/internal/delivery/http"
	repository "github.com/scribe-security/scribe2/scribe-service/internal/repository/pg"
	service "github.com/scribe-security/scribe2/scribe-service/internal/service"
	"github.com/scribe-security/scribe2/scribe-service/internal/version"
	"github.com/scribe-security/scribe2/scribe-service/pkg/config"
	"github.com/scribe-security/scribe2/scribe-service/pkg/connection"
	"github.com/scribe-security/scribe2/scribe-service/pkg/etl"
	fss3 "github.com/scribe-security/scribe2/scribe-service/pkg/fstore/s3"
	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
	"github.com/scribe-security/scribe2/scribe-service/pkg/server"
)

var serverCmd = &cobra.Command{
	Use: "server",
	Run: func(cmd *cobra.Command, args []string) {
		runServer(cmd.Context())
	},
}

func init() {
	rootCmd.AddCommand(serverCmd)
}

func setupModules(
	cfg *config.Config,
	app *fiber.App,
	conn *sqlx.DB,
	ac *aws.Config,
) {
	// Repository Layer
	evstrepo := repository.NewPgEvidenceRepository(conn)
	fs := fss3.New(ac, cfg.FileTransfers.BucketName)

	etlService := etl.New(cfg.Airflow)

	// service Layer
	svc := service.New(fs, evstrepo, etlService, cfg.FileTransfers, cfg.Environment)

	// Delivery Layer
	// internal groups
	internal := app.Group("/internal")
	ievstrg := internal.Group("/evidence")

	// route groups
	evstrg := app.Group("/evidence")

	app.Get(
		"/health",
		adaptor.HTTPHandlerFunc(Health),
	)

	// handlers setup their own router
	delivery.NewEVSTHandler(evstrg, svc, &cfg.Auth0)

	// internal handlers
	delivery.NewEVSTInternalHandler(ievstrg, svc)
	app.Post(
		githubapp.DefaultWebhookRoute,
		adaptor.HTTPHandler(
			githubapp.NewDefaultEventDispatcher(
				cfg.Github,
				github.New(github.CreateHandlerParameters{
					Service: svc,
				}))))
}

type NoOpRateLimit struct{}

func (NoOpRateLimit) AddTokens(uint) error { return nil }
func (NoOpRateLimit) GetToken(context.Context, uint) (func() error, error) {
	return noOpToken, nil
}
func noOpToken() error { return nil }

func runServer(ctx context.Context) {
	ctx, cancelFunc := context.WithCancel(ctx)
	defer cancelFunc()

	l := log.L(ctx)

	// TODO: change logger interface to match new interfaces
	l.Info("Loading scribe-service api service", zap.String("Version", version.GetVersion()))

	// Config
	cfg, err := config.New()
	if err != nil {
		l.Fatal("unable to load config", zap.Error(err))
	}

	l.Info("config loaded", zap.String("env_name", cfg.Environment))

	// Postgres
	postgresClient := connection.NewPostgres(ctx, cfg.Postgres.String())
	defer postgresClient.Close()

	// HTTP
	port := ":4000"
	fsrv := server.NewFiberServer(server.FiberConfig{
		Port: port,
		Name: "mono",
	})

	// AWS
	// TODO: improve wrapper
	ac, err := awsc.LoadDefaultConfig(
		ctx,
		awsc.WithRegion(cfg.FileTransfers.DefaultRegion),
		awsc.WithRetryer(func() aws.Retryer {
			return retry.NewStandard(func(o *retry.StandardOptions) {
				o.MaxAttempts = 20
				o.RateLimiter = NoOpRateLimit{}
			})
		}))
	if err != nil {
		l.Fatal("unable to load SDK config", zap.Error(err))
	}

	// Setup
	setupModules(
		cfg,
		fsrv.Server,
		postgresClient,
		&ac,
	)

	// Serve Fiber
	go fsrv.ListenAndServe(ctx)

	// Graceful
	// TODO: use framework for graceful shutdown (+include listeners for database/asynq/etc..)
	interruptChan := make(chan os.Signal, 1)

	signal.Notify(interruptChan, os.Interrupt, syscall.SIGINT, syscall.SIGTERM)
	<-interruptChan
	l.Info("gracefully shutting down")

	cancelFunc()
	fsrv.Shutdown(ctx)
}

func Health(w http.ResponseWriter, _ *http.Request) {
	w.WriteHeader(http.StatusOK)
}
