package s3

import (
	"context"
	"fmt"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"go.uber.org/zap"

	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

// FileStore implementation file store interface for S3.
type FileStore struct {
	s3c        *s3.Client
	psc        *s3.PresignClient
	bucketName string
}

// New S3 file store interface
func New(cfg *aws.Config, bucketName string) *FileStore {
	s3c := s3.NewFromConfig(*cfg)
	psc := s3.NewPresignClient(s3c)
	return &FileStore{
		s3c:        s3c,
		psc:        psc,
		bucketName: bucketName,
	}
}

// GetUploadURL to put file to storage.
func (s *FileStore) GetUploadURL(
	ctx context.Context, fileName string,
) (string, error) {
	l := log.L(ctx).Logger().With(
		zap.String("bucket", s.bucketName), zap.String("file_name", fileName))

	input := s3.PutObjectInput{
		Key:    &fileName,
		Bucket: &s.bucketName,
	}

	preq, err := s.psc.PresignPutObject(ctx, &input)
	if err != nil {
		l.Error("presign upload URL", zap.Error(err))
		return "", fmt.Errorf("presign upload URL: %w", err)
	}

	return preq.URL, nil
}

// GetDownloadURL for file from the storage.
func (s *FileStore) GetDownloadURL(
	ctx context.Context, fileName string,
) (string, error) {
	l := log.L(ctx).Logger().
		With(zap.String("bucket", s.bucketName), zap.String("file_name", fileName))
	input := s3.GetObjectInput{
		Key:    &fileName,
		Bucket: &s.bucketName,
	}

	preq, err := s.psc.PresignGetObject(ctx, &input)
	if err != nil {
		l.Error("presign download URL", zap.Error(err))
		return "", fmt.Errorf("presign download URL: %w", err)
	}

	return preq.URL, nil
}

// GetBucketName using to put/get file.
func (s *FileStore) GetBucketName() string {
	return s.bucketName
}

// GetStorageType implemented by this storer.
func (s *FileStore) GetStorageType() string {
	return "s3"
}

func (s *FileStore) GetFileSize(ctx context.Context, fileName string) (int, error) {
	headObj := s3.HeadObjectInput{
		Key:    &fileName,
		Bucket: &s.bucketName,
	}
	result, err := s.s3c.HeadObject(ctx, &headObj)
	if err != nil {
		return 0, err
	}
	return int(result.ContentLength), nil
}
