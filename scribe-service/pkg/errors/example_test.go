package errors_test

import (
	"fmt"

	"github.com/scribe-security/scribe2/scribe-service/pkg/errors"
)

func ExampleNew() {
	err := errors.New("whoops")
	fmt.Println(err)

	// Output: whoops
}

func ExampleNew_printf() {
	err := errors.New("whoops")
	fmt.Printf("%+v", err)

	// Example output:
	// whoops
	// github.com/scribe-security/scribe2/scribe-service/pkg/errors_test.ExampleNew_printf
	//         /home/john/src/github.com/scribe-security/scribe2/scribe-service/pkg/errors/example_test.go:17
	// testing.runExample
	//         /home/john/go/src/testing/example.go:114
	// testing.RunExamples
	//         /home/john/go/src/testing/example.go:38
	// testing.(*M).Run
	//         /home/john/go/src/testing/testing.go:744
	// main.main
	//         /github.com/scribe-security/scribe2/scribe-service/pkg/errors/_test/_testmain.go:106
	// runtime.main
	//         /home/john/go/src/runtime/proc.go:183
	// runtime.goexit
	//         /home/john/go/src/runtime/asm_amd64.s:2059
}

func ExampleWrap() {
	cause := errors.New("whoops")
	err := errors.Wrap(cause, "oh noes")
	fmt.Println(err)

	// Output: oh noes: whoops
}

func fn() error {
	e1 := errors.New("error")
	e2 := errors.Wrap(e1, "inner")
	e3 := errors.Wrap(e2, "middle")
	return errors.Wrap(e3, "outer")
}

func ExampleWrap_extended() {
	err := fn()
	fmt.Printf("%+v\n", err)

	// Example output:
	// error
	// github.com/scribe-security/scribe2/scribe-service/pkg/errors_test.fn
	//         /home/john/src/github.com/scribe-security/scribe2/scribe-service/pkg/errors/example_test.go:47
	// github.com/scribe-security/scribe2/scribe-service/pkg/errors_test.ExampleCause_printf
	//         /home/john/src/github.com/scribe-security/scribe2/scribe-service/pkg/errors/example_test.go:63
	// testing.runExample
	//         /home/john/go/src/testing/example.go:114
	// testing.RunExamples
	//         /home/john/go/src/testing/example.go:38
	// testing.(*M).Run
	//         /home/john/go/src/testing/testing.go:744
	// main.main
	//         /github.com/scribe-security/scribe2/scribe-service/pkg/errors/_test/_testmain.go:104
	// runtime.main
	//         /home/john/go/src/runtime/proc.go:183
	// runtime.goexit
	//         /home/john/go/src/runtime/asm_amd64.s:2059
	// github.com/scribe-security/scribe2/scribe-service/pkg/errors_test.fn
	// 	  /home/john/src/github.com/scribe-security/scribe2/scribe-service/pkg/errors/example_test.go:48: inner
	// github.com/scribe-security/scribe2/scribe-service/pkg/errors_test.fn
	//        /home/john/src/github.com/scribe-security/scribe2/scribe-service/pkg/errors/example_test.go:49: middle
	// github.com/scribe-security/scribe2/scribe-service/pkg/errors_test.fn
	//      /home/john/src/github.com/scribe-security/scribe2/scribe-service/pkg/errors/example_test.go:50: outer
}

func ExampleWrapf() {
	cause := errors.New("whoops")
	err := errors.Wrapf(cause, "oh noes #%d", 2)
	fmt.Println(err)

	// Output: oh noes #2: whoops
}

func ExampleErrorf_extended() {
	err := errors.Errorf("whoops: %s", "foo")
	fmt.Printf("%+v", err)

	// Example output:
	// whoops: foo
	// github.com/scribe-security/scribe2/scribe-service/pkg/errors_test.ExampleErrorf
	//         /home/john/src/github.com/scribe-security/scribe2/scribe-service/pkg/errors/example_test.go:101
	// testing.runExample
	//         /home/john/go/src/testing/example.go:114
	// testing.RunExamples
	//         /home/john/go/src/testing/example.go:38
	// testing.(*M).Run
	//         /home/john/go/src/testing/testing.go:744
	// main.main
	//         /github.com/scribe-security/scribe2/scribe-service/pkg/errors/_test/_testmain.go:102
	// runtime.main
	//         /home/john/go/src/runtime/proc.go:183
	// runtime.goexit
	//         /home/john/go/src/runtime/asm_amd64.s:2059
}

func Example_stackTrace() {
	type stackTracer interface {
		StackTrace() errors.StackTrace
	}

	err, ok := errors.Unwrap(fn()).(stackTracer)
	if !ok {
		panic("oops, err does not implement stackTracer")
	}

	st := err.StackTrace()
	fmt.Printf("%+v", st[0:2]) // top two frames

	// Example output:
	// github.com/scribe-security/scribe2/scribe-service/pkg/errors_test.fn
	//	/home/john/src/github.com/scribe-security/scribe2/scribe-service/pkg/errors/example_test.go:47
	// github.com/scribe-security/scribe2/scribe-service/pkg/errors_test.Example_stackTrace
	//	/home/john/src/github.com/scribe-security/scribe2/scribe-service/pkg/errors/example_test.go:127
}
