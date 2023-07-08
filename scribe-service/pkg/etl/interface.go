package etl

import "context"

type Airflow interface {
	TriggerETL(ctx context.Context, etlName string, payload []byte) error
}
