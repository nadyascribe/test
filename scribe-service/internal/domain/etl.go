package domain

type TriggerETLPayload interface {
	TriggerETLPayload()
	EtlName() string
	GetPayload() (map[string]interface{}, error)
}
