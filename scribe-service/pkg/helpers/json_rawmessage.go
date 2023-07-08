package helpers

import (
	"encoding/json"

	"github.com/containerd/containerd/log"
)

func NewRawJSON(c interface{}) *json.RawMessage {
	out, err := json.Marshal(c)
	if err != nil {
		log.L.Errorf("Failed on marshal with error :%v", err)
	}
	rs := json.RawMessage(out)
	return &rs
}
