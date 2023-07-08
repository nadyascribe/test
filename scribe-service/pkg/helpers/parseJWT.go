package helpers

import (
	"fmt"

	"github.com/golang-jwt/jwt"
)

// token structs for future helpers if required

// m2m token
type GensbomClaims struct {
	jwt.StandardClaims
	UserID           string `json:"azp,omitempty"`
	TeamName         string `json:"https://scribe-security/team-name,omitempty"`
	TeamCreatorEmail string `json:"https://scribe-security/team-creator-email,omitempty"`
}

// user token
type FrontendClaims struct {
	jwt.StandardClaims
	Email string `json:"email,omitempty"`
}

func TokenM2MExtractUserID(token *string) (userID string, err error) {
	if token == nil {
		return "", fmt.Errorf("token is null reference")
	}

	parser := jwt.Parser{
		SkipClaimsValidation: true,
	}

	userClaims := FrontendClaims{}
	_, _, err = parser.ParseUnverified(*token, &userClaims)
	if err != nil {
		return "", fmt.Errorf("m2m token parse failed")
	}

	m2mClaims := GensbomClaims{}
	_, _, err = parser.ParseUnverified(*token, &m2mClaims)
	if err != nil {
		return "", fmt.Errorf("m2m token parse failed")
	}

	if userClaims.Email != "" {
		userID = userClaims.Audience
	} else {
		userID = m2mClaims.UserID
	}

	return userID, nil
}
