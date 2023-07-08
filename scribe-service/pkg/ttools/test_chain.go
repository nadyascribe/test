package ttools

import (
	"context"
	"fmt"
	"path"
	"runtime"
	"testing"

	"github.com/go-testfixtures/testfixtures/v3"
	"github.com/jmoiron/sqlx"
	"github.com/testcontainers/testcontainers-go"
	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/pkg/config"
	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
	"github.com/scribe-security/scribe2/scribe-service/pkg/migrator"
	"github.com/scribe-security/scribe2/scribe-service/pkg/seeder"
	"github.com/scribe-security/scribe2/scribe-service/pkg/testcontainer"
)

// TestChain tool which helps use real db and fixtures in the tests.
//
// If you init this helper tool in the test main function it will do this:
//   - create container with PostgreSQL
//   - run migrations over this PostgreSQL
//   - prepares fixtures
//
// Example with fixtures:
// ```
// ...
// var testChain *ttools.TestChain
//
//	func TestMain(m *testing.M) {
//	    testChain = ttools.NewTestChain(
//	        context.Background(), m, "projects.yaml", "users.yaml")
//	    os.Exit(testChain.Start().Close())
//	}
//
// ...
// ```
//
// Example of test methods with prepared fixtures:
// ```
// ...
//
//	func TestQueries(t *testing.T) {
//	    testChain.WithFixtures(t, func(db *sqlx.DB) {
//	        // Now this DB also contains temporary fixtures.
//	    })
//	}
//
// ```
type TestChain struct {
	m          *testing.M
	ctx        context.Context
	db         *sqlx.DB
	err        error
	container  testcontainers.Container
	loader     *testfixtures.Loader
	fixtures   []string
	resultCode int
}

// NewTestChain instance constructor.
func NewTestChain(ctx context.Context, m *testing.M, fixtures ...string) *TestChain {
	return &TestChain{
		ctx:        ctx,
		m:          m,
		resultCode: 1,
		fixtures:   fixtures,
	}
}

// Run all tests.
//
// This method is wrapper for m.Run method and must be used instead it.
func (tc *TestChain) Run() *TestChain {
	container, db, err := testcontainer.CreateTestContainer(tc.ctx, "testdb")
	if err != nil {
		log.L().Error("create test container", zap.Error(err))
		tc.err = fmt.Errorf("create test container: %w", err)
		return tc
	}
	tc.container = container
	tc.db = db

	mig, err := migrator.NewPgMigrator(db)
	if err != nil {
		log.L().Error("create migrator", zap.Error(err))
		tc.err = fmt.Errorf("create migrator: %w", err)
		return tc
	}

	if err = mig.Up(); err != nil {
		log.L().Error("run migration to latest version", zap.Error(err))
		tc.err = fmt.Errorf("run migration to latest version: %w", err)
		return tc
	}

	cfg, err := config.New()
	if err != nil {
		log.L().Error("seed database", zap.Error(err))
		tc.err = fmt.Errorf("seed database: %w", err)
		return tc
	}
	// TODO: move data from seeder into fixtures
	if err := seeder.New(cfg.Environment, db).Seed(); err != nil {
		log.L().Error("seed database", zap.Error(err))
		tc.err = fmt.Errorf("seed database: %w", err)
		return tc
	}

	if err := tc.loadFixtures(); err != nil {
		log.L().Error("init fixtures", zap.Error(err))
		tc.err = fmt.Errorf("init fixtures: %w", err)
		return tc
	}

	tc.resultCode = tc.m.Run()
	return tc
}

// Close test container and connection to database.
//
// We not join this method to Run to save ability extend after test actions.
func (tc *TestChain) Close() int {
	if tc.db != nil {
		if err := tc.db.Close(); err != nil {
			log.L().Warn("failed to close db connection", zap.Error(err))
		}
	}

	if tc.container != nil {
		if err := tc.container.Terminate(tc.ctx); err != nil {
			log.L().Warn("failed to terminate the test container", zap.Error(err))
		}
	}

	if tc.err != nil {
		log.L().Error("error init test", zap.Error(tc.err))
	}

	return tc.resultCode
}

// WithFixtures uploads fixtures and runs test function.
func (tc *TestChain) WithFixtures(t *testing.T, fn func(db *sqlx.DB)) {
	if err := tc.loader.Load(); err != nil {
		t.Errorf("load fixtures %v", err)
		return
	}

	fn(tc.db)
}

func (tc *TestChain) loadFixtures() error {
	basePath := tc.getFixturesPath()
	for i := range tc.fixtures {
		tc.fixtures[i] = fmt.Sprintf("%s/%s", basePath, tc.fixtures[i])
	}

	loader, err := testfixtures.New(
		testfixtures.DangerousSkipTestDatabaseCheck(),
		testfixtures.Database(tc.db.DB),
		testfixtures.Dialect("postgres"),
		testfixtures.Files(tc.fixtures...),
	)
	if err != nil {
		return err
	}
	tc.loader = loader
	return nil
}

func (tc *TestChain) getFixturesPath() string {
	_, filename, _, _ := runtime.Caller(1) //nolint
	return fmt.Sprintf("%s/../../fixtures", path.Dir(filename))
}
