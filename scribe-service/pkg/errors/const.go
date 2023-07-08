package errors

// NewConst returns a simple error without any annotated context, like stack trace.
//
//	var ErrSomething = errors.NewConst("something went wrong")
func NewConst(message string, opts ...Option) error {
	return applyOptions(&constError{msg: message}, opts...)
}

type Option func(err *constError)

func DontLogAsError() Option {
	return func(err *constError) {
		err.dontLog = true
	}
}

func applyOptions(err *constError, opts ...Option) *constError {
	for _, o := range opts {
		o(err)
	}
	return err
}

// constError is a trivial implementation of error.
type constError struct {
	msg     string
	dontLog bool
}

func (e *constError) Error() string {
	return e.msg
}

func (e *constError) DontLogAsError() bool {
	return e.dontLog
}
