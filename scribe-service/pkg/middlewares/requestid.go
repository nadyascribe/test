package middlewares

import (
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/requestid"
)

func RequestID() func(*fiber.Ctx) error {
	return requestid.New(requestid.Config{
		Header:     "X-B3-TraceId",
		ContextKey: "traceid",
	})
}
