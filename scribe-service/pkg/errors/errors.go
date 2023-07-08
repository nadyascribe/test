package errors

import (
	stderrors "errors"
	"fmt"
	"io"
)

// New returns an error with the supplied message.
// New also records the stack trace at the point it was called.
func New(message string) error {
	return &fundamentalError{
		msg:   message,
		stack: callers(),
	}
}

// Errorf formats according to a format specifier and returns the string
// as a value that satisfies error.
// Errorf also records the stack trace at the point it was called.
func Errorf(format string, args ...interface{}) error {
	return &fundamentalError{
		msg:   fmt.Sprintf(format, args...),
		stack: callers(),
	}
}

// fundamentalError is an error that has a message and a stack, but no caller.
type fundamentalError struct {
	msg string
	*stack
}

func (f *fundamentalError) Error() string { return f.msg }

func (f *fundamentalError) Format(s fmt.State, verb rune) {
	switch verb {
	case 'v':
		if s.Flag('+') {
			_, _ = io.WriteString(s, f.msg)
			f.stack.Format(s, verb)
			return
		}
		fallthrough
	case 's':
		_, _ = io.WriteString(s, f.msg)
	case 'q':
		fmt.Fprintf(s, "%q", f.msg)
	}
}

type withStackError struct {
	error
	*stack
}

// Unwrap provides compatibility for Go 1.13 error chains.
func (w *withStackError) Unwrap() error { return w.error }

func (w *withStackError) Format(s fmt.State, verb rune) {
	switch verb {
	case 'v':
		if s.Flag('+') {
			fmt.Fprintf(s, "%+v", w.Unwrap())
			w.stack.Format(s, verb)
			return
		}
		fallthrough
	case 's':
		_, _ = io.WriteString(s, w.Error())
	case 'q':
		fmt.Fprintf(s, "%q", w.Error())
	}
}

// Wrap returns an error annotating err with a stack trace
// at the point Wrap is called, and the supplied message.
// If err is nil, Wrap returns nil.
// If known stack-traced errors detected in errors chain,
// do not append new stack trace.
// If no messages, only stack attaches (if needed).
func Wrap(err error, messages ...string) error {
	if err == nil {
		return nil
	}
	for _, m := range messages {
		if m == "" {
			continue
		}
		err = &withMessageError{
			cause: err,
			msg:   m,
		}
	}
	var se stackTracedError
	if As(err, &se) {
		return err
	}
	return &withStackError{
		err,
		callers(),
	}
}

// BasedOn works like Wrap, but does not provide traceback of original error.
func BasedOn(err error, messages ...string) error {
	if err == nil {
		panic("hot nil error")
	}
	for _, m := range messages {
		if m == "" {
			continue
		}
		err = &withMessageError{
			cause: err,
			msg:   m,
		}
	}
	return err
}

// Wrapf returns an error annotating err with a stack trace
// at the point Wrapf is called, and the format specifier.
// If err is nil, Wrapf returns nil.
func Wrapf(err error, format string, args ...interface{}) error {
	if err == nil {
		return nil
	}
	err = &withMessageError{
		cause: err,
		msg:   fmt.Sprintf(format, args...),
	}
	var se stackTracedError
	if As(err, &se) {
		return err
	}
	return &withStackError{
		err,
		callers(),
	}
}

type withMessageError struct {
	cause error
	msg   string
}

func (w *withMessageError) Error() string { return w.msg + ": " + w.cause.Error() }

// Unwrap provides compatibility for Go 1.13 error chains.
func (w *withMessageError) Unwrap() error { return w.cause }

func (w *withMessageError) Format(s fmt.State, verb rune) {
	switch verb {
	case 'v':
		if s.Flag('+') {
			fmt.Fprintf(s, "%+v\n", w.Unwrap())
			_, _ = io.WriteString(s, w.msg)
			return
		}
		fallthrough
	case 's':
		_, _ = io.WriteString(s, w.Error())
	case 'q':
		fmt.Fprintf(s, "%q", w.Error())
	}
}

// Is works like standard errors.Is(), but checks multiple targets.
func Is(err, first error, others ...error) bool {
	for _, t := range append(others, first) {
		if stderrors.Is(err, t) {
			return true
		}
	}
	return false
}

// As works like standard errors.As().
func As(err error, target interface{}) bool {
	return stderrors.As(err, target)
}

// Unwrap works like standard errors.Unwrap().
func Unwrap(err error) error {
	return stderrors.Unwrap(err)
}
