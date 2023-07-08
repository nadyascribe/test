package errors

import (
	"fmt"
	"runtime"
	"testing"

	"go.uber.org/multierr"
)

var initpc = caller()

type X struct{}

// val returns a Frame pointing to itself.
func (x X) val() Frame {
	return caller()
}

// ptr returns a Frame pointing to itself.
func (x *X) ptr() Frame {
	return caller()
}

func TestFrameFormat(t *testing.T) {
	tests := []struct {
		Frame
		format string
		want   string
	}{{
		initpc,
		"%s",
		"stack_test.go",
	}, {
		initpc,
		"%+s",
		"github.com/scribe-security/scribe2/scribe-service/pkg/errors.init\n" +
			"\t.+/errors/stack_test.go",
	}, {
		0,
		"%s",
		"unknown",
	}, {
		0,
		"%+s",
		"unknown",
	}, {
		initpc,
		"%d",
		"11",
	}, {
		0,
		"%d",
		"0",
	}, {
		initpc,
		"%n",
		"init",
	}, {
		func() Frame {
			var x X
			return x.ptr()
		}(),
		"%n",
		`\(\*X\).ptr`,
	}, {
		func() Frame {
			var x X
			return x.val()
		}(),
		"%n",
		"X.val",
	}, {
		0,
		"%n",
		"",
	}, {
		initpc,
		"%v",
		"stack_test.go:11",
	}, {
		initpc,
		"%+v",
		"github.com/scribe-security/scribe2/scribe-service/pkg/errors.init\n" +
			"\t.+/errors/stack_test.go:11",
	}, {
		0,
		"%v",
		"unknown:0",
	}}

	for i, tt := range tests {
		testFormatRegexp(t, i, tt.Frame, tt.format, tt.want)
	}
}

func TestFuncname(t *testing.T) {
	tests := []struct {
		name, want string
	}{
		{"", ""},
		{"runtime.main", "main"},
		{"github.com/scribe-security/scribe2/scribe-service/pkg/errors.funcname", "funcname"},
		{"funcname", "funcname"},
		{"io.copyBuffer", "copyBuffer"},
		{"main.(*R).Write", "(*R).Write"},
	}

	for _, tt := range tests {
		got := funcname(tt.name)
		want := tt.want
		if got != want {
			t.Errorf("funcname(%q): want: %q, got %q", tt.name, want, got)
		}
	}
}

func TestStackTrace(t *testing.T) {
	tests := []struct {
		err  error
		want []string
	}{{
		New("ooh"), []string{
			"github.com/scribe-security/scribe2/scribe-service/pkg/errors.TestStackTrace\n" +
				"\t.+/errors/stack_test.go:123",
		},
	}, {
		Wrap(New("ooh"), "ahh"), []string{
			"github.com/scribe-security/scribe2/scribe-service/pkg/errors.TestStackTrace\n" +
				"\t.+/errors/stack_test.go:128", // this is the stack of Wrap, not New
		},
	}, {
		Unwrap(Wrap(New("ooh"), "ahh")), []string{
			"github.com/scribe-security/scribe2/scribe-service/pkg/errors.TestStackTrace\n" +
				"\t.+/errors/stack_test.go:133", // this is the stack of New
		},
	}, {
		func() error { return New("ooh") }(), []string{
			`github.com/scribe-security/scribe2/scribe-service/pkg/errors.TestStackTrace.func1` +
				"\n\t.+/errors/stack_test.go:138", // this is the stack of New
			"github.com/scribe-security/scribe2/scribe-service/pkg/errors.TestStackTrace\n" +
				"\t.+/errors/stack_test.go:138", // this is the stack of New's caller
		},
	}, {
		func() error {
			return func() error {
				return Errorf("hello %s", fmt.Sprintf("world: %s", "ooh"))
			}()
		}(), []string{
			`github.com/scribe-security/scribe2/scribe-service/pkg/errors.TestStackTrace.func2.1` +
				"\n\t.+/errors/stack_test.go:147", // this is the stack of Errorf
			`github.com/scribe-security/scribe2/scribe-service/pkg/errors.TestStackTrace.func2` +
				"\n\t.+/errors/stack_test.go:148", // this is the stack of Errorf's caller
			"github.com/scribe-security/scribe2/scribe-service/pkg/errors.TestStackTrace\n" +
				"\t.+/errors/stack_test.go:149", // this is the stack of Errorf's caller's caller
		},
	}}
	for i, tt := range tests {
		var se interface {
			StackTrace() StackTrace
		}
		if !As(tt.err, &se) {
			t.Errorf("expected %#v to implement StackTrace() StackTrace", tt.err)
			continue
		}
		st := se.StackTrace()
		for j, want := range tt.want {
			testFormatRegexp(t, i, st[j], "%+v", want)
		}
	}
}

func stackTrace() StackTrace {
	const depth = 8
	var pcs [depth]uintptr
	n := runtime.Callers(1, pcs[:])
	var st stack = pcs[0:n]
	return st.StackTrace()
}

func TestStackTraceFormat(t *testing.T) {
	tests := []struct {
		StackTrace
		format string
		want   string
	}{{
		nil,
		"%s",
		`\[\]`,
	}, {
		nil,
		"%v",
		`\[\]`,
	}, {
		nil,
		"%+v",
		"",
	}, {
		nil,
		"%#v",
		`\[\]errors.Frame\(nil\)`,
	}, {
		make(StackTrace, 0),
		"%s",
		`\[\]`,
	}, {
		make(StackTrace, 0),
		"%v",
		`\[\]`,
	}, {
		make(StackTrace, 0),
		"%+v",
		"",
	}, {
		make(StackTrace, 0),
		"%#v",
		`\[\]errors.Frame{}`,
	}, {
		stackTrace()[:2],
		"%s",
		`\[stack_test.go stack_test.go\]`,
	}, {
		stackTrace()[:2],
		"%v",
		`\[stack_test.go:176 stack_test.go:223\]`,
	}, {
		stackTrace()[:2],
		"%+v",
		"\n" +
			"github.com/scribe-security/scribe2/scribe-service/pkg/errors.stackTrace\n" +
			"\t.+/errors/stack_test.go:176\n" +
			"github.com/scribe-security/scribe2/scribe-service/pkg/errors.TestStackTraceFormat\n" +
			"\t.+/errors/stack_test.go:227",
	}, {
		stackTrace()[:2],
		"%#v",
		`\[\]errors.Frame{stack_test.go:176, stack_test.go:235}`,
	}}

	for i, tt := range tests {
		testFormatRegexp(t, i, tt.StackTrace, tt.format, tt.want)
	}
}

// a version of runtime.Caller that returns a Frame, not a uintptr.
func caller() Frame {
	var pcs [3]uintptr
	n := runtime.Callers(2, pcs[:])
	frames := runtime.CallersFrames(pcs[:n])
	frame, _ := frames.Next()
	return Frame(frame.PC)
}

func TestMultipleWraps(t *testing.T) {
	tests := []struct {
		err    error
		stacks int
	}{
		{
			Wrap(Wrap(New("error"), "wrap1"), "wrap2"),
			1,
		},
		{
			Wrap(Wrap(NewConst("error"), "wrap1"), "wrap2"),
			1,
		},
	}

	for _, tt := range tests {
		got := GetStackTraces(tt.err)
		if len(got) != tt.stacks {
			t.Errorf("invalid stacks count (%d != %d)", len(got), tt.stacks)
		}
	}
}

func TestGetStacks(t *testing.T) {
	err := Wrap(
		multierr.Combine(New("error1"), New("error2")),
		"wrap",
	)

	stacks := GetStackTraces(err)

	if got := len(stacks); got != 2 {
		t.Errorf("invalid stacks count (%d)", got)
	}
}
