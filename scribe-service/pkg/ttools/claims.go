package ttools

import (
	"context"

	jwtmiddleware "github.com/auth0/go-jwt-middleware"
	"github.com/auth0/go-jwt-middleware/validate/josev2"
	"gopkg.in/square/go-jose.v2/jwt"

	"github.com/scribe-security/scribe2/scribe-service/internal/domain"
)

// CtxWithUserClaims updates context with user claims only for test purposes.
func CtxWithUserClaims(ctx context.Context, userID string, productKeys []string) context.Context {
	customClaims := domain.CustomClaims{
		ProductKeys: productKeys,
	}
	return context.WithValue(
		ctx,
		jwtmiddleware.ContextKey{},
		&josev2.UserContext{
			Claims: jwt.Claims{
				Subject: userID,
			},
			CustomClaims: &customClaims,
		},
	)
}
