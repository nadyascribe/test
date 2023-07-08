package log

import (
	"context"
	"os"

	zaplogfmt "github.com/sykesm/zap-logfmt"
	"github.com/uptrace/opentelemetry-go-extra/otelzap"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

func New() *otelzap.Logger {
	logger := otelzap.New(zap.L(),
		otelzap.WithTraceIDField(true),
		otelzap.WithMinLevel(zap.DebugLevel))

	otelzap.ReplaceGlobals(logger)
	return logger
}

func L(ctx ...context.Context) *otelzap.LoggerWithCtx {
	var c context.Context
	if len(ctx) > 0 {
		c = ctx[0]
	}

	l := otelzap.Ctx(c)
	return &l
}

func S(ctx ...context.Context) *otelzap.SugaredLoggerWithCtx {
	var c context.Context
	if len(ctx) > 0 {
		c = ctx[0]
	}
	return SugaredWithCtx(c)
}

func SugaredWithCtx(ctx context.Context) *otelzap.SugaredLoggerWithCtx {
	ctxl := otelzap.S().Ctx(ctx)
	return &ctxl
}

// unify with other internal framework lib
func Setup(debug bool) {
	var logger *zap.Logger
	cfg := zap.NewProductionEncoderConfig()
	level := zapcore.InfoLevel
	if debug {
		level = zapcore.DebugLevel
	}

	logger = zap.New(zapcore.NewCore(
		zaplogfmt.NewEncoder(cfg),
		os.Stdout,
		level,
	), zap.AddCaller(), zap.AddStacktrace(zap.ErrorLevel))

	//nolint
	defer logger.Sync() // flushes buffer, if any

	zap.ReplaceGlobals(logger)
	New()
}
