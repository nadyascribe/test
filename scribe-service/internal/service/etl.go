package service

import (
	"context"
	"encoding/json"

	"github.com/scribe-security/scribe2/scribe-service/internal/domain"
	"github.com/scribe-security/scribe2/scribe-service/pkg/errors"
)

func (s *service) TriggerETL(ctx context.Context, in domain.TriggerETLPayload) error {
	dagRunConf, err := in.GetPayload()
	if err != nil {
		return errors.Wrap(err, "failed to get payload")
	}

	reqData := map[string]interface{}{"conf": dagRunConf}

	payload, err := json.Marshal(&reqData)
	if err != nil {
		return errors.Wrap(err, "failed to marshal payload")
	}

	return s.etl.TriggerETL(ctx, in.EtlName(), payload)
}
