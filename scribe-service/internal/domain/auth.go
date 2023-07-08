package domain

import (
	"context"
)

// CustomClaims from id_token.
type CustomClaims struct {
	ProductKeys []string `json:"https://scribe-security/pkeys"`
}

// Validate user custom claims.
func (c *CustomClaims) Validate(_ context.Context) error {
	return nil
}
