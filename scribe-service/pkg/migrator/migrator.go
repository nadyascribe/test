package migrator

import (
	"path/filepath"
	"runtime"

	"github.com/golang-migrate/migrate/v4"
	"github.com/golang-migrate/migrate/v4/database/postgres"
	_ "github.com/golang-migrate/migrate/v4/source/file" // need for migration
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq" // need for pg

	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

func NewPgMigrator(db *sqlx.DB) (*migrate.Migrate, error) {
	_, path, _, ok := runtime.Caller(0)
	if !ok {
		log.S().Fatalf("failed to get path")
	}

	sourceURL := "file://" + filepath.Dir(path) + "/../../migrations"

	driver, err := postgres.WithInstance(db.DB, &postgres.Config{})
	if err != nil {
		log.S().Fatalf("failed to create migrator driver: %s", err)
	}

	m, err := migrate.NewWithDatabaseInstance(sourceURL, "postgres", driver)

	return m, err
}
