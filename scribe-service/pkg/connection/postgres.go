package connection

import (
	"context"

	"github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/stdlib"
	"github.com/jmoiron/sqlx"

	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

// NewPostgres
// TODO: consider return value of NewPostgres (now returns sqlx.DB, maybe a pool or a struct wrapping it all. we'll see)
func NewPostgres(ctx context.Context, uri string) *sqlx.DB {
	dcfg, err := pgx.ParseConfig(uri)
	if err != nil {
		log.S(ctx).Fatalf("unable to parse postgres connection string: %v", err.Error())
	}

	conn, err := sqlx.NewDb(stdlib.OpenDB(*dcfg), "pgx"), nil
	if err != nil {
		log.S(ctx).Fatalf("socket server unexpected error %v", err)
	}

	return conn
}
