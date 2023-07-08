package fstore

import (
	"context"
)

// FileStorer interface to access uploaded storages.
//
//go:generate mockgen -destination=mocks/mock_file_storer.go -package=mocks . FileStorer
type FileStorer interface {
	// GetUploadURL to put file to storage.
	//
	// Method returns presigned URL for file upload.
	GetUploadURL(ctx context.Context, fileName string) (string, error)

	// GetDownloadURL for file from the storage.
	GetDownloadURL(ctx context.Context, fileName string) (string, error)

	// GetBucketName using to put/get file.
	GetBucketName() string

	// GetStorageType implemented by this storer.
	GetStorageType() string

	// GetFileSize returns file size in bytes
	GetFileSize(ctx context.Context, fileName string) (int, error)
}
