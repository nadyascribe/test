package transport

import (
	"encoding/json"

	"github.com/gofiber/fiber/v2"

	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

// ResponseError represent the reseponse error struct
// swagger:response errorResponse
type ResponseError struct {
	HTTPStatus int    `json:"-"`
	Status     int    `json:"status"`
	Message    string `json:"message"`
}

type ResponseMessage struct {
	Message string `json:"message,omitempty"`
}

func (e *ResponseError) WriteToResponse(c *fiber.Ctx) error {
	if _, err := c.Status(e.HTTPStatus).WriteString(e.ToJSON()); err != nil {
		log.S(c.UserContext()).Errorf("unable to send json response: %v", err)
		return err
	}

	return nil
}

func (e *ResponseError) ToJSON() string {
	j, err := json.Marshal(e)
	if err != nil {
		return `{"code":50001,"message":"unable to marshal error"}`
	}
	return string(j)
}
