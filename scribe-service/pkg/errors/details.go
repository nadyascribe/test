package errors

import "fmt"

// Detail is error details.
type Detail struct {
	// Detail key.
	Key string
	// Detail value.
	Value interface{}
}

type (
	D       = Detail
	Details []Detail
)

// detailedError is interface for detailed errors.
type detailedError interface {
	Details() Details
}

type withDetailsError struct {
	cause   error
	details Details
}

// WithDetails annotates err with arbitrary key-value pairs.
//
//	var DetailedError = errors.WithDetails(err,
//		D{"key", "value"},
//		D{"other_key": "other_value"},
//	)
func WithDetails(err error, details ...Detail) error {
	if err == nil {
		return nil
	}

	if len(details) == 0 {
		return err
	}

	return &withDetailsError{
		cause:   err,
		details: details,
	}
}

// Details returns the appended details.
func (w *withDetailsError) Details() Details {
	return w.details
}

func (w *withDetailsError) Error() string {
	return w.cause.Error()
}

func (w *withDetailsError) Unwrap() error {
	return w.cause
}

func (w *withDetailsError) Format(s fmt.State, verb rune) {
	switch verb {
	case 'v':
		if s.Flag('+') {
			_, _ = fmt.Fprintf(s, "%+v", w.cause)
			return
		}

		_, _ = fmt.Fprintf(s, "%v", w.cause)

	case 's':
		_, _ = fmt.Fprintf(s, "%s", w.cause)

	case 'q':
		_, _ = fmt.Fprintf(s, "%q", w.cause)
	}
}
