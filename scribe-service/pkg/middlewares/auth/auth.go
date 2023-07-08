package auth

import (
	"fmt"
	"net/http"
	"net/url"
	"time"

	jwtmiddleware "github.com/auth0/go-jwt-middleware"
	"github.com/auth0/go-jwt-middleware/validate/josev2"
	"github.com/gofiber/adaptor/v2"
	"github.com/gofiber/fiber/v2"
	"gopkg.in/square/go-jose.v2"
	"gopkg.in/square/go-jose.v2/jwt"

	"github.com/scribe-security/scribe2/scribe-service/internal/domain"
	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

var timeout = 5 * time.Minute

// TODO: user scopes: https://auth0.com/docs/quickstart/backend/golang/01-authorization
func New(auth0Domain string, config ...Config) fiber.Handler {
	issuerURL := fmt.Sprintf("https://%s/", auth0Domain)

	u, err := url.Parse(issuerURL)
	if err != nil {
		log.S().Fatalf("there was an error with parsing issuerURL: %v %v", issuerURL, err.Error())
	}

	p := josev2.NewCachingJWKSProvider(*u, timeout)

	cfg := configDefault(config...)
	// TODO: improve, add ignores
	expectedClaimsFunc := func() jwt.Expected {
		return jwt.Expected{
			Issuer:   fmt.Sprintf("https://%s/", auth0Domain),
			Audience: jwt.Audience(cfg.Audience),
		}
	}

	errHandler := func(w http.ResponseWriter, r *http.Request, err error) {
		log.S().Infof("error in token validation: %v\n", err)

		jwtmiddleware.DefaultErrorHandler(w, r, err)
	}

	validator, err := josev2.New(
		p.KeyFunc,
		jose.RS256,
		josev2.WithExpectedClaims(expectedClaimsFunc),
		josev2.WithCustomClaims(func() josev2.CustomClaims {
			return &domain.CustomClaims{}
		}),
	)
	if err != nil {
		log.S().Fatalf("there was an error creating a new validator %v", err.Error())
	}

	m := jwtmiddleware.New(validator.ValidateToken, jwtmiddleware.WithErrorHandler(errHandler))
	return HTTPMiddleware(m.CheckJWT)
}

// NOTE: we are copying the HTTPMiddleware adaptor because the request context doesn't get propegated to fiber context
func HTTPMiddleware(mw func(http.Handler) http.Handler) fiber.Handler {
	return func(c *fiber.Ctx) error {
		var next bool
		nextHandler := http.HandlerFunc(func(_ http.ResponseWriter, r *http.Request) {
			next = true
			// Convert again in case request may modify by middleware
			c.Request().Header.SetMethod(r.Method)
			c.Request().SetRequestURI(r.RequestURI)
			c.Request().SetHost(r.Host)
			for key, val := range r.Header {
				for _, v := range val {
					c.Request().Header.Set(key, v)
				}
			}

			reqCtx := r.Context().Value(jwtmiddleware.ContextKey{})
			c.SetUserContext(r.Context())
			c.Locals("user", reqCtx)
		})
		_ = adaptor.HTTPHandler(mw(nextHandler))(c)
		if next {
			return c.Next()
		}
		return nil
	}
}
