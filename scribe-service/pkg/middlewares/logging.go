package middlewares

import (
	"context"
	"time"

	"github.com/hibiken/asynq"
	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

func Logging(h asynq.Handler) asynq.Handler {
	return asynq.HandlerFunc(func(ctx context.Context, t *asynq.Task) error {
		l := log.L(ctx).Logger().With(zap.String("task", t.Type()))
		start := time.Now()
		l.Debug("start processing")
		err := h.ProcessTask(ctx, t)
		if err != nil {
			return err
		}
		l.Debug("finished processing", zap.Duration("elapsed_time", time.Since(start)))
		return nil
	})
}
