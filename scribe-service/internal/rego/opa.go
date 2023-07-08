package rego

import (
	"context"
	"encoding/json"

	"github.com/open-policy-agent/opa/rego"
	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/pkg/errors"
	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

func ExecuteOpa(ctx context.Context, policyPath, regoQuery string, inputParams interface{}) ([]byte, error) {
	logger := log.L(ctx)

	r, err := rego.New(
		rego.LoadBundle(policyPath),
		rego.Query(regoQuery),
		rego.EnablePrintStatements(true),
	).PrepareForEval(ctx)
	if err != nil {
		logger.Error("Error creating new rego object", zap.Error(err))
		return nil, err
	}

	// Run evaluation.
	rs, err := r.Eval(ctx, rego.EvalInput(inputParams))
	if err != nil {
		logger.Error("Error evaluating organization policy", zap.Error(err))
		return nil, err
	}

	// Inspect results.
	if rs != nil && rs[0].Expressions != nil && rs[0].Expressions[0].Value != nil {
		jsonResult, err := json.MarshalIndent(rs[0].Expressions[0].Value, "", "  ")
		if err != nil {
			logger.Error("Error marshaling the rego expression", zap.Error(err))
			return nil, errors.Wrap(err)
		}
		logger.Debug("got data")
		return jsonResult, nil
	}

	logger.Warn("Policy result not available", zap.Any("result", rs))

	return nil, nil
}
