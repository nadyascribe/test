package errors

import (
	"reflect"
	"testing"

	"go.uber.org/multierr"
)

func TestWithDetailsFormat(t *testing.T) {
	origErr := NewConst("something went wrong")
	details := []Detail{{"key", "value"}}
	err := WithDetails(origErr, details...)

	t.Run("error_message", func(t *testing.T) {
		checkErrorMessage(t, err, "something went wrong")
	})

	t.Run("unwrap", func(t *testing.T) {
		checkUnwrap(t, err, origErr)
	})

	t.Run("format", func(t *testing.T) {
		checkFormat(t, err, map[string][]string{
			"%s":  {"something went wrong"},
			"%q":  {`"something went wrong"`},
			"%v":  {"something went wrong"},
			"%+v": {"something went wrong"},
		})
	})

	t.Run("nil", func(t *testing.T) {
		checkErrorNil(t, WithDetails(nil, Detail{"key", "value"}))
	})

	t.Run("details", func(t *testing.T) {
		d := err.(*withDetailsError).Details()

		for i, detail := range d {
			if got, want := detail, details[i]; got != want {
				t.Errorf("error detail does not match the expected one\nactual:   %+v\nexpected: %+v", got, want)
			}
		}
	})
}

func TestGetDetails(t *testing.T) {
	err := WithDetails(
		WithDetails(
			Wrap(
				multierr.Combine(
					WithDetails(
						New("error1"), Detail{"str", "value1"},
					),
					WithDetails(
						New("error2"), Detail{"str", "value2"},
					),
				),
				"wrapped error",
			), Detail{"int", 999},
		), Detail{"obj", struct {
			f1 bool
			f2 float64
		}{true, 2.345}},
	)

	expected := []Detail{
		{"str", "value1"},
		{"str", "value2"},
		{"int", 999},
		{"obj", struct {
			f1 bool
			f2 float64
		}{true, 2.345}},
	}

	actual := GetDetails(err)

	if got, want := actual, expected; !reflect.DeepEqual(got, want) {
		t.Errorf("context does not match the expected one\nactual:   %v\nexpected: %v", got, want)
	}
}

func TestEmptyDetails(t *testing.T) {
	err := WithDetails(NewConst("error"))
	if actual := GetDetails(err); actual != nil {
		t.Errorf("context does not match the expected one\nactual:   %v\nexpected: %v", actual, nil)
	}
}

func TestUnwrapEach(t *testing.T) {
	err := Wrap(
		WithDetails(
			NewConst("error"),
			Detail{"key", "value"},
		), "message",
	)

	detailsFound := false
	UnwrapEach(err, func(err error) bool {
		se := &withStackError{}
		if As(err, &se) {
			return false
		}

		de := &withDetailsError{}
		if As(err, &de) {
			detailsFound = true
		}
		return true
	})

	if detailsFound {
		t.Error("step down too deep")
	}
}
