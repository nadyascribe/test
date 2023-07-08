package auth

import (
	"github.com/gofiber/fiber/v2"
)

// Config defines the config for middleware.
type Config struct {
	// Next defines a function to skip this middleware when returned true.
	//
	// Optional. Default: nil
	Next func(c *fiber.Ctx) bool

	// ContextKey defines the key used when storing the user ID in
	// the locals for a specific request.
	//
	// Optional. Default: userID
	ContextKey string

	//
	//
	// Optional. Default: false
	IgnoreAudience bool

	//
	//
	// Optional. Default: userID
	Audience []string

	//
	//
	// Optional. Default: false
	IgnoreIssuer bool
}

// ConfigDefault is the default config
func newConfigDefault() *Config {
	return &Config{
		Next:           nil,
		Audience:       []string{},
		IgnoreAudience: false,
		IgnoreIssuer:   false,
		ContextKey:     "userID",
	}
}

// Helper function to set default values
func configDefault(config ...Config) Config {
	// Return default config if nothing provided
	if len(config) < 1 {
		return *newConfigDefault()
	}

	// Override default config
	cfg := config[0]
	defCfg := newConfigDefault()

	// Set default values
	if cfg.ContextKey == "" {
		cfg.ContextKey = defCfg.ContextKey
	}

	if len(cfg.Audience) == 0 {
		cfg.Audience = defCfg.Audience
	}

	return cfg
}
