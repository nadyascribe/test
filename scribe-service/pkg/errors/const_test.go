package errors_test

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/scribe-security/scribe2/scribe-service/pkg/errors"
)

func TestDontLogAsError(t *testing.T) {
	var i interface {
		DontLogAsError() bool
	}

	var (
		errDanger = errors.NewConst("danger")
		errValid  = errors.NewConst("dont log me", errors.DontLogAsError())
	)

	require.True(t, errors.As(errDanger, &i))
	assert.False(t, i.DontLogAsError())

	require.True(t, errors.As(errValid, &i))
	assert.True(t, i.DontLogAsError())
}
