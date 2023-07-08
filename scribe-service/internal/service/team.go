package service

import (
	"context"

	"github.com/golang-jwt/jwt"
	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

// GetTeamID returns the team ID for the m2m jwt subject if team exists in DB, etherwise returns error
func (s *service) GetTeamID(
	ctx context.Context,
	token *string,
) (teamID int64, err error) {
	claims, err := ParseToken(ctx, token)
	if err != nil {
		log.L(ctx).Error("parse token error", zap.Error(err))
		return 0, err
	}

	// check if team exists
	teamID, err = s.r.GetTeamIDByTokenSub(ctx, claims.Subject)
	if err != nil {
		log.L(ctx).Error("get team by token sub", zap.Error(err),
			zap.String("claims.Subject", claims.Subject))
		return 0, err
	}

	return teamID, nil
}

// GetTeamName returns user team name from token
func (s *service) GetTeamName(
	ctx context.Context,
	token *string,
) (string, error) {
	claims, err := ParseToken(ctx, token)
	if err != nil {
		log.L(ctx).Error("parse token", zap.Error(err))
		return "", err
	}

	return claims.TeamName, nil
}

type CustomClaims struct {
	jwt.StandardClaims
	UserID           string `json:"azp,omitempty"`
	Email            string `json:"email,omitempty"`
	TeamName         string `json:"https://scribe-security/team-name,omitempty"`
	TeamCreatorEmail string `json:"https://scribe-security/team-creator-email,omitempty"`
}

// ParseToken parses the token and returns the claims.
func ParseToken(ctx context.Context, tokenString *string) (*CustomClaims, error) {
	parser := jwt.Parser{
		SkipClaimsValidation: true,
	}

	myClaims := CustomClaims{}

	// the token was already verified by fiber in the handler, no need to verify again
	_, _, err := parser.ParseUnverified(*tokenString, &myClaims)
	if err != nil {
		log.L(ctx).Error("ParseUnverified token parse failed", zap.Error(err))
		return nil, err
	}

	return &myClaims, nil
}
