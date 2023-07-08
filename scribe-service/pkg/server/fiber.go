package server

import (
	"context"
	"net/http"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"

	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
	"github.com/scribe-security/scribe2/scribe-service/pkg/middlewares"
)

// FiberConfig defines the config for fiber server.
type FiberConfig struct {
	// Port
	Port string

	// Name
	Name string
}

// newFiberConfigDefault is the default config, it loads defaults from env/config files
func newFiberConfigDefault() *FiberConfig {
	return &FiberConfig{
		Port: ":4000",
		Name: "api",
	}
}

type FiberServer struct {
	Config *FiberConfig
	Server *fiber.App
}

func NewFiberServer(fcfg ...FiberConfig) *FiberServer {
	cfg := newFiberConfigDefault()
	if len(fcfg) > 0 {
		// TODO: merge fcfg with default vaules
		cfg = &fcfg[0]
	}

	app := fiber.New()

	// setup default middlewares
	app.Use(cors.New())
	app.Use(middlewares.RequestID())

	return &FiberServer{
		Server: app,
		Config: cfg,
	}
}

func (fs *FiberServer) ListenAndServe(ctx context.Context) {
	if err := fs.Server.Listen(fs.Config.Port); err != nil {
		log.S(ctx).Infof("HTTP server shutting down")
		if err != http.ErrServerClosed {
			log.S(ctx).Fatalf("closed unexpected error %v", err)
		}
	}
}

func (fs *FiberServer) Shutdown(ctx context.Context) {
	if err := fs.Server.Shutdown(); err != nil {
		log.S(ctx).Infof("HTTP server shutting down")
	}
}
