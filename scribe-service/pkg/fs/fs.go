package pkgfs

import (
	"context"
	"fmt"
	"os"
	"path/filepath"

	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

// createTempDir creates temporary directory for SBOM file and returns cleanup function which
// you must call when you are done with the directory
func CreateTempDir(
	ctx context.Context,
	fileID int,
) (tempDir string, cleanup func(), err error) {
	tempDir = filepath.Join(os.TempDir(), fmt.Sprintf("scribe-%d", fileID))
	modeDir := os.ModeDir | 0o755
	if err = os.Mkdir(tempDir, modeDir); err != nil {
		log.L(ctx).Error("create temporary dir", zap.Error(err))
		return "", nil, err
	}
	return tempDir, func() {
		if err := os.RemoveAll(tempDir); err != nil {
			log.L(ctx).Error("remove temp dir", zap.Error(err))
		}
	}, nil
}
