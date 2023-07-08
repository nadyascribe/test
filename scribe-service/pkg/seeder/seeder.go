package seeder

import (
	"fmt"
	"os"
	"path"
	"runtime"

	"github.com/jmoiron/sqlx"
)

type Seeder struct {
	db  *sqlx.DB
	env string
}

//nolint:revive
func New(env string, db *sqlx.DB) *Seeder {
	return &Seeder{
		db: db,
	}
}

func (s *Seeder) Seed(name ...string) error {
	var sname string
	if len(name) > 0 {
		sname = name[0]
	} else {
		sname = fmt.Sprintf("%s.sql", s.env)
	}
	// TODO: use env + make seed file name as input
	q, err := os.ReadFile(GetSourcePath() + sname)
	if err != nil {
		return err
	}

	_, err = s.db.Exec(string(q))
	if err != nil {
		return err
	}

	// Revert CVE protection to allow 'public' as search path
	_, err = s.db.Exec("SELECT pg_catalog.set_config('search_path', 'public', FALSE)")
	if err != nil {
		return err
	}

	return nil
}

func GetSourcePath() string {
	//nolint:dogsled
	_, filename, _, _ := runtime.Caller(1)
	return fmt.Sprintf("%s/../../seeds/", path.Dir(filename))
}
