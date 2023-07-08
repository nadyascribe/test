//go:build unit
// +build unit

package repository_test

import (
	"context"
	"encoding/json"
	"os"
	"testing"
	"time"

	"github.com/auth0/go-jwt-middleware/validate/josev2"
	"github.com/google/go-cmp/cmp"
	"github.com/jmoiron/sqlx"
	"gopkg.in/square/go-jose.v2/jwt"

	"github.com/scribe-security/scribe2/scribe-service/internal/domain"
	ftrp "github.com/scribe-security/scribe2/scribe-service/internal/repository/pg"
	"github.com/scribe-security/scribe2/scribe-service/pkg/ttools"
)

const testBase = "PgFileTransfersRepository"

var testChain *ttools.TestChain

func TestMain(m *testing.M) {
	testChain = ttools.NewTestChain(context.Background(), m, "file_transfers_files.yaml")

	// Use this logger initialization if need to see the logs of initialization process.
	ttools.InitLogger()
	os.Exit(testChain.Run().Close())
}

func TestNewPgFileTransfersRepository_CreateFileTransfer(t *testing.T) {
	tests := []struct {
		Name     string
		Context  context.Context
		Input    *domain.CreateFileTransfer
		Attrs    *domain.FileTransferAttributes
		MustFail bool
	}{
		{
			Name:    "Success File Transfer",
			Context: context.TODO(),
			Input: &domain.CreateFileTransfer{
				Key:    "/path/to/file",
				UserID: "fake_user_id",
			},
			Attrs: &domain.FileTransferAttributes{
				Bucket:       "filetransfers",
				CloudStorage: "s3",
			},
			MustFail: false,
		},
		{
			Name:    "Same key, same user, should rewrite",
			Context: context.TODO(),
			Input: &domain.CreateFileTransfer{
				Key:    "/path/to/file",
				UserID: "fake_user_id",
			},
			Attrs: &domain.FileTransferAttributes{
				Bucket:       "filetransfers",
				CloudStorage: "s3",
			},
			MustFail: false,
		},
		{
			Name:    "Same key, different user, should return error",
			Context: context.TODO(),
			Input: &domain.CreateFileTransfer{
				Key:    "/path/to/file",
				UserID: "fake_user_id2",
			},
			Attrs: &domain.FileTransferAttributes{
				Bucket:       "filetransfers",
				CloudStorage: "s3",
			},
			MustFail: true,
		},
		{
			Name:    "No key field",
			Context: context.TODO(),
			Input: &domain.CreateFileTransfer{
				UserID: "fake_user_id",
			},
			Attrs: &domain.FileTransferAttributes{
				Bucket:       "filetransfers",
				CloudStorage: "s3",
			},
			MustFail: true,
		},
		{
			Name:    "No bucket field",
			Context: context.TODO(),
			Input: &domain.CreateFileTransfer{
				Key:    "/path/to/file",
				UserID: "fake_user_id",
			},
			Attrs: &domain.FileTransferAttributes{
				CloudStorage: "s3",
			},
			MustFail: true,
		},
	}

	testChain.WithFixtures(t, func(db *sqlx.DB) {
		for _, tt := range tests {
			t.Run(tt.Name, func(t *testing.T) {
				fileID, err := ftrp.
					NewPgFileTransfersRepository(db).
					CreateFileTransfer(tt.Context, tt.Input, tt.Attrs)
				if (err != nil) != tt.MustFail {
					t.Errorf("%s.CreateFileTransfer() error = %v", testBase, err)
					return
				}
				if (fileID == 0) != tt.MustFail {
					t.Errorf("%s.CreateFileTransfer() file ID can't be 0", testBase)
					return
				}
			})
		}
	})
}

func TestNewPgFileTransfersRepository_ListFileTransfers(t *testing.T) {
	tests := []struct {
		Name        string
		Input       domain.ListFileTransfersInput
		ExpectCount int
		MustFail    bool
	}{
		{
			Name: "Select matchone group",
			Input: domain.ListFileTransfersInput{
				Key:          "%/matchone/%",
				Bucket:       "bucket1",
				CloudStorage: "s3",
				UserID:       "fake_user_id",
			},
			ExpectCount: 3,
			MustFail:    false,
		},
		{
			Name: "Select matchtwo group",
			Input: domain.ListFileTransfersInput{
				Key:          "/path/to/matchtwo/%",
				Bucket:       "bucket1",
				CloudStorage: "s3",
				UserID:       "fake_user_id",
			},
			ExpectCount: 2,
			MustFail:    false,
		},
	}

	testChain.WithFixtures(t, func(db *sqlx.DB) {
		repo := ftrp.NewPgFileTransfersRepository(db)
		for _, tt := range tests {
			list, err := repo.ListFileTransfers(context.TODO(), &tt.Input)
			if (err != nil) != tt.MustFail {
				t.Errorf("%s.ListFileTransfers() call error = %v", testBase, err)
				return
			}
			if (len(list) != tt.ExpectCount) != tt.MustFail {
				t.Errorf(
					"%s.ListFileTransfers() call wrong items count returned: expected %v, got %v",
					testBase, tt.ExpectCount, len(list))
				return
			}
		}
	})
}

func TestNewPgFileTransfersRepository_FinishFileTransfer(t *testing.T) {
	metadataStr := `{"key1" : "value1", "key2" : "value2"}`
	contextObj, err := json.Marshal(metadataStr)
	if err != nil {
		t.Errorf("error marshaling the context json: %v", err)
		return
	}

	tests := []struct {
		Name     string
		Input    *domain.FinishFileTransfer
		MustFail bool
	}{
		{
			Name: "Finish successfully",
			Input: &domain.FinishFileTransfer{
				FileID: 7,
				UserID: "fake_user_id",
			},
			MustFail: false,
		},
		{
			Name: "Already uploaded",
			Input: &domain.FinishFileTransfer{
				FileID: 8,
				UserID: "fake_user_id",
			},
			MustFail: true,
		},
		{
			Name: "Finish successfully",
			Input: &domain.FinishFileTransfer{
				FileID:      9,
				UserID:      "fake_user_id",
				ContentType: "attestation",
				ContextType: "github",
				ContextData: contextObj,
			},
			MustFail: false,
		},
	}

	testChain.WithFixtures(t, func(db *sqlx.DB) {
		repo := ftrp.NewPgFileTransfersRepository(db)
		user := &josev2.UserContext{Claims: jwt.Claims{Subject: "1"}}
		testContext := context.WithValue(context.TODO(), "user", user)

		for _, tt := range tests {
			err := repo.FinishFileTransfer(testContext, tt.Input)
			if (err != nil) != tt.MustFail {
				t.Errorf("%s.FinishFileTransfer() call error = %v", testBase, err)
				return
			}

			if tt.Input.FileID == 3 {
				file, err := repo.GetFileTransferByID(testContext, tt.Input.FileID)
				if err != nil {
					t.Errorf(
						"%s.FinishFileTransfer() error finding file by id : %v",
						testBase, err)
				}

				if file == nil || file.ContentType != "attestation" ||
					file.ContextType != "github" {
					t.Errorf(
						"%s.FinishFileTransfer() unexpected file data = %v",
						testBase, file)
				}
			}
		}
	})
}

func TestNewPgFileTransfersRepository_DeleteFileTransfers(t *testing.T) {
	tests := []struct {
		Name     string
		Context  context.Context
		Input    domain.DeleteEvidenceInput
		Deleted  int
		MustFail bool
	}{
		{
			Name:    "Delete file transfer by file ID",
			Context: context.TODO(),
			Input: domain.DeleteEvidenceInput{
				FileID: ttools.IntRef(6),
				UserID: "fake_user_id",
			},
			Deleted:  1,
			MustFail: false,
		},
		{
			Name:    "Delete files by key pattern",
			Context: context.TODO(),
			Input: domain.DeleteEvidenceInput{
				Key:          ttools.StrRef("/path/to/matchone%"),
				Bucket:       ttools.StrRef("bucket1"),
				CloudStorage: ttools.StrRef("s3"),
				UserID:       "fake_user_id",
			},
			Deleted:  3,
			MustFail: false,
		},
	}

	testChain.WithFixtures(t, func(db *sqlx.DB) {
		repo := ftrp.NewPgFileTransfersRepository(db)
		for _, tt := range tests {
			totalCount := 0
			err := db.
				QueryRow("SELECT count(*) FROM file_transfers_files").
				Scan(&totalCount)
			if err != nil {
				t.Errorf(
					"%s.DeleteFileTransfers() get count of items = %v", testBase, err)
				return
			}

			if err := repo.DeleteFileTransfers(tt.Context, &tt.Input); err != nil {
				if tt.MustFail {
					continue
				}
				t.Errorf("%s.DeleteFileTransfers() call error = %v", testBase, err)
				return
			}

			var count int
			err = db.
				QueryRow("SELECT count(*) FROM file_transfers_files").
				Scan(&count)
			if err != nil {
				t.Errorf(
					"%s.DeleteFileTransfers() get count of items = %v", testBase, err)
				return
			}

			if removedCount := totalCount - count; removedCount != tt.Deleted {
				t.Errorf(
					"%s.DeleteFileTransfers() deleted items count expected = %d, got = %d",
					testBase, tt.Deleted, removedCount)
				return
			}
		}
	})
}

func TestNewPgFileTransfersRepository_GetFileTransferByID(t *testing.T) {
	t1, err := time.Parse("2006-01-02 15:04:05", "2021-07-14 09:27:20")
	if err != nil {
		t.Errorf("parse time: %v", err)
		return
	}

	tests := []struct {
		Name     string
		Input    int
		Output   *domain.FileTransferBase
		MustFail bool
	}{
		{
			Name:  "get file transfer by file ID",
			Input: 2,
			Output: &domain.FileTransferBase{
				FileID:       2,
				Key:          "/path/to/matchone/file2",
				Bucket:       "bucket1",
				CloudStorage: "s3",
				UserID:       "fake_user_id",
				Status:       "uploaded",
				Lock:         domain.FileTransferFreeLock,
				CreatedAt:    t1,
			},
			MustFail: false,
		},
		{
			Name:     "get file transfer not exists",
			Input:    -1,
			Output:   nil,
			MustFail: true,
		},
	}

	testChain.WithFixtures(t, func(db *sqlx.DB) {
		repo := ftrp.NewPgFileTransfersRepository(db)
		for _, tt := range tests {
			fo, err := repo.GetFileTransferByID(context.TODO(), tt.Input)
			if err != nil {
				if tt.MustFail {
					continue
				}
				t.Errorf("%s.GetFileTransferByID() call error = %v", testBase, err)
				continue
			}

			if fo == nil {
				if tt.Output != nil {
					t.Errorf(
						"%s.GetFileTransferByID() returns nil, but expected = %v",
						testBase, tt.Output)
				}
				continue
			}

			tt.Output.UpdatedAt = fo.UpdatedAt
			if !cmp.Equal(fo, tt.Output) {
				t.Errorf(
					"%s.GetFileTransferByID() expected = %+v, got = %+v",
					testBase, tt.Output, fo)
			}
		}
	})
}

func TestNewPgFileTransfersRepository_GetFileTransferByKey(t *testing.T) {
	t1, err := time.Parse("2006-01-02 15:04:05", "2021-07-14 09:27:20")
	if err != nil {
		t.Errorf("parse time: %v", err)
		return
	}

	tests := []struct {
		Name     string
		Input    string
		Output   *domain.FileTransferBase
		MustFail bool
	}{
		{
			Name:  "get file transfer by key",
			Input: "/path/to/matchone/file2",
			Output: &domain.FileTransferBase{
				FileID:       2,
				Key:          "/path/to/matchone/file2",
				Bucket:       "bucket1",
				CloudStorage: "s3",
				UserID:       "fake_user_id",
				Status:       "uploaded",
				Lock:         domain.FileTransferFreeLock,
				CreatedAt:    t1,
			},
			MustFail: false,
		},
		{
			Name:     "get file transfer by key not exists",
			Input:    "__NOT_EXISTS__",
			Output:   nil,
			MustFail: false,
		},
	}

	testChain.WithFixtures(t, func(db *sqlx.DB) {
		repo := ftrp.NewPgFileTransfersRepository(db)
		for _, tt := range tests {
			fo, err := repo.GetFileTransferByKey(
				context.TODO(),
				tt.Input,
				&domain.FileTransferAttributes{
					Bucket:       "bucket1",
					CloudStorage: "s3",
				},
			)
			if err != nil {
				if tt.MustFail {
					continue
				}
				t.Errorf("%s.GetFileTransferByKey() call error = %v", testBase, err)
				continue
			}
			if fo == nil {
				if tt.Output != nil {
					t.Errorf(
						"%s.GetFileTransferByKey() returns nil, but expected = %v",
						testBase, tt.Output)
				}
				continue
			}

			tt.Output.UpdatedAt = fo.UpdatedAt
			if !cmp.Equal(fo, tt.Output) {
				t.Errorf(
					"%s.GetFileTransferByKey() expected = %v, got = %v",
					testBase, tt.Output, fo)
			}
		}
	})
}

func TestNewPgFileTransfersRepository_SetFileTransferLock(t *testing.T) {
	tests := []struct {
		Name       string
		Context    context.Context
		Input      domain.SetFileTransferLockInput
		ExpectLock domain.FileTransferLockType
		MustFail   bool
	}{
		{
			Name:    "Set lock",
			Context: context.TODO(),
			Input: domain.SetFileTransferLockInput{
				FileID: 1,
				Lock:   domain.FileTransferReadLock,
				UserID: "fake_user_id",
			},
			ExpectLock: domain.FileTransferReadLock,
			MustFail:   false,
		},
	}

	testChain.WithFixtures(t, func(db *sqlx.DB) {
		repo := ftrp.NewPgFileTransfersRepository(db)
		for _, tt := range tests {
			err := repo.SetFileTransferLock(tt.Context, &tt.Input)
			if err != nil {
				if tt.MustFail {
					continue
				}
				t.Errorf("%s.SetFileTransferLock() call error = %v", testBase, err)
				return
			}

			var lock string
			err = db.
				QueryRow(
					`SELECT "lock" FROM file_transfers_files WHERE file_id=$1`,
					tt.Input.FileID).
				Scan(&lock)
			if err != nil {
				t.Errorf(
					"%s.SetFileTransferLock() get status of item = %v", testBase, err)
				return
			}

			if lock != string(tt.ExpectLock) {
				t.Errorf(
					"%s.SetFileTransferLock() item lock expected = %s, got = %s",
					testBase, tt.ExpectLock, lock)
				return
			}
		}
	})
}

func TestPgFileTransfersRepository_CreateFileTransferWithMetadata(t *testing.T) {
	var metadata struct {
		Name    string `json:"name"`
		ImageID string `json:"imageID"`
	}
	metadata.Name = "testname"
	metadata.ImageID = "1234"
	metadataBytes, err := json.Marshal(metadata)
	if err != nil {
		t.Fatal("error marshaling metadata: ", err)
	}

	tests := []struct {
		Name     string
		Context  context.Context
		Input    *domain.UploadEvidenceFileTransfer
		Attrs    *domain.FileTransferAttributes
		MustFail bool
	}{
		{
			Name:    "Success File Transfer",
			Context: context.TODO(),
			Input: &domain.UploadEvidenceFileTransfer{
				Key:         "/path/to/file",
				UserID:      "fake_user_id",
				ContentType: "cyclonedx-json",
				ContextType: "local",
				ContextData: metadataBytes,
			},
			Attrs: &domain.FileTransferAttributes{
				Bucket:       "filetransfers",
				CloudStorage: "s3",
			},
			MustFail: false,
		},
		{
			Name:    "Same key, same user, should rewrite",
			Context: context.TODO(),
			Input: &domain.UploadEvidenceFileTransfer{
				Key:         "/path/to/file",
				UserID:      "fake_user_id",
				ContentType: "cyclonedx-json",
				ContextType: "local",
				ContextData: metadataBytes,
			},
			Attrs: &domain.FileTransferAttributes{
				Bucket:       "filetransfers",
				CloudStorage: "s3",
			},
			MustFail: false,
		},
		{
			Name:    "Same key, different user, should return error",
			Context: context.TODO(),
			Input: &domain.UploadEvidenceFileTransfer{
				Key:         "/path/to/file",
				UserID:      "fake_user_id2",
				ContentType: "cyclonedx-json",
				ContextType: "local",
				ContextData: metadataBytes,
			},
			Attrs: &domain.FileTransferAttributes{
				Bucket:       "filetransfers",
				CloudStorage: "s3",
			},
			MustFail: true,
		},
		{
			Name:    "No key field",
			Context: context.TODO(),
			Input: &domain.UploadEvidenceFileTransfer{
				Key:         "",
				UserID:      "fake_user_id",
				ContentType: "cyclonedx-json",
				ContextType: "local",
				ContextData: metadataBytes,
			},
			Attrs: &domain.FileTransferAttributes{
				Bucket:       "filetransfers",
				CloudStorage: "s3",
			},
			MustFail: true,
		},
		{
			Name:    "No bucket field",
			Context: context.TODO(),
			Input: &domain.UploadEvidenceFileTransfer{
				Key:         "/path/to/file",
				UserID:      "fake_user_id",
				ContentType: "cyclonedx-json",
				ContextType: "local",
				ContextData: metadataBytes,
			},
			Attrs: &domain.FileTransferAttributes{
				CloudStorage: "s3",
			},
			MustFail: true,
		},
	}

	testChain.WithFixtures(t, func(db *sqlx.DB) {
		for _, tt := range tests {
			t.Run(tt.Name, func(t *testing.T) {
				fileID, err := ftrp.
					NewPgFileTransfersRepository(db).
					CreateFileTransferWithMetadata(tt.Context, tt.Input, tt.Attrs)
				if (err != nil) != tt.MustFail {
					t.Errorf("%s.CreateFileTransfer() error = %v", testBase, err)
					return
				}
				if (fileID == 0) != tt.MustFail {
					t.Errorf("%s.CreateFileTransfer() file ID can't be 0", testBase)
					return
				}
			})
		}
	})
}
