package errors

import "testing"

func checkErrorMessage(t *testing.T, err error, message string) {
	t.Helper()

	if got, want := err.Error(), message; got != want {
		t.Errorf("error message does not match the expectd\nactual:   %s\nexpected: %s", got, want)
	}
}

func checkUnwrap(t *testing.T, err, origErr error) {
	t.Helper()

	if err, ok := err.(interface{ Unwrap() error }); ok {
		if got, want := err.Unwrap(), origErr; got != want {
			t.Errorf("error does not match the expected one\nactual:   %#v\nexpected: %#v", got, want)
		}
	} else {
		t.Fatal("error does not implement the wrapper (interface{ Unwrap() error}) interface")
	}
}

func checkErrorNil(t *testing.T, err error) {
	t.Helper()

	if err != nil {
		t.Errorf("nil error is expected to result in nil\nactual: %#v", err)
	}
}

func checkFormat(t *testing.T, err error, formats map[string][]string) {
	t.Helper()

	i := 1

	for format, want := range formats {
		testFormatCompleteCompare(t, i, err, format, want, true)

		i++
	}
}
