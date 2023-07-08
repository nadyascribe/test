package helpers

import (
	"context"
	"errors"
	"fmt"

	jwtmiddleware "github.com/auth0/go-jwt-middleware"
	"github.com/auth0/go-jwt-middleware/validate/josev2"

	"github.com/scribe-security/scribe2/scribe-service/internal/domain"
)

func GetUserID(ctx context.Context) (userID string) {
	if usrCtx := ctx.Value(jwtmiddleware.ContextKey{}); usrCtx != nil {
		userID = usrCtx.(*josev2.UserContext).Claims.ID
		if userID == "" {
			userID = usrCtx.(*josev2.UserContext).Claims.Subject
		}
	}

	return userID
}

// GetProductKey from the SPA and M2M claims.
func GetProductKey(ctx context.Context) (string, error) {
	if userCtx := ctx.Value(jwtmiddleware.ContextKey{}); userCtx != nil {
		userClaims, ok := userCtx.(*josev2.UserContext).CustomClaims.(*domain.CustomClaims)
		if ok && len(userClaims.ProductKeys) > 0 {
			return userClaims.ProductKeys[len(userClaims.ProductKeys)-1], nil // TODO: we need active project claim to fix that
		}
		return "", fmt.Errorf("unknown claims")
	}
	return "", fmt.Errorf("no user context")
}

// GetAudience list from the JWT token claims
func GetAudience(ctx context.Context) (audience string, err error) {
	userCtx := ctx.Value(jwtmiddleware.ContextKey{})
	if userCtx != nil {
		var audiences []string = userCtx.(*josev2.UserContext).Claims.Audience
		if audiences == nil || len(audiences) != 1 {
			// As discussed with Givi returning error in case we have multiple
			// audiences. Need to revisit this
			return "", errors.New("invalid audience values in claims")
		}
		return audiences[0], nil
	}
	return "", errors.New("missing user context")
}
