package service

import (
	"github.com/scribe-security/scribe2/scribe-service/internal/domain"
	"github.com/scribe-security/scribe2/scribe-service/pkg/config"
	"github.com/scribe-security/scribe2/scribe-service/pkg/etl"
	"github.com/scribe-security/scribe2/scribe-service/pkg/fstore"
)

type service struct {
	fst fstore.FileStorer
	r   domain.EvidenceStoreRepository
	cfg config.FileTransfers
	env string
	etl etl.Airflow
}

// New instance constructor.
func New(
	fst fstore.FileStorer,
	r domain.EvidenceStoreRepository,
	etlService etl.Airflow,
	cfg config.FileTransfers,
	environment string,
) domain.EvidenceStoreService {
	return &service{
		fst: fst,
		r:   r,
		etl: etlService,
		cfg: cfg,
		env: environment,
	}
}
