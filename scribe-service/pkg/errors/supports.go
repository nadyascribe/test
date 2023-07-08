package errors

import "go.uber.org/multierr"

// UnwrapEach loops through an error chain and calls a function for each of them.
// The provided function can return false to break the loop before it reaches the end of the chain.
func UnwrapEach(err error, fn func(err error) bool) {
	for err != nil {
		continueLoop := fn(err)
		if !continueLoop {
			break
		}

		err = Unwrap(err)
	}
}

// GetStackTraces extracts set of stack-traces from all errors in chain.
func GetStackTraces(err error) []StackTrace {
	var stacks []StackTrace

	UnwrapEach(err, func(err error) bool {
		errs := multierr.Errors(err)
		for _, e := range errs {
			if ste, ok := e.(stackTracedError); ok {
				stacks = append(stacks, ste.StackTrace())
			}
		}

		return true
	})

	return stacks
}

// GetDetails extracts the key-value pairs from err's chain.
func GetDetails(err error) []Detail {
	var details []Detail

	UnwrapEach(err, func(err error) bool {
		errs := multierr.Errors(err)
		for i := len(errs) - 1; i >= 0; i-- {
			if de, ok := errs[i].(detailedError); ok {
				details = append(de.Details(), details...)
			}
		}

		return true
	})

	return details
}
