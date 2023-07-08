package ttools

import (
	"bytes"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"
)

// HTTPFixture request/resonse object for expected behavior of the mocked HTTP server
type HTTPFixture struct {
	// URL relative path to match the mocked request
	URL string
	// Method of HTTP call which should be mocked
	Method string
	// Request body content
	Request []byte
	// ResponseCode which should be returned for mocked request
	ResponseCode int
	// Response body content
	Response []byte
}

// WithMockedHTTPServer runs test HTTP servera and uses the list of playFixtures to serve requests
//
// Each request should sequentally match to the playFixtures slice element, else it fails.
// If request query matches to fixture, response of this fixture will be returned as HTTP body
// with fixture status code.
//
// In the testFunc for the all test reuests must be used srv.Client() HTTP client
// and all request must have as base URL srv.URL()
func WithMockedHTTPServer(
	t *testing.T,
	playFixtures []HTTPFixture,
	testFunc func(srv *httptest.Server),
) {
	// for each fixture we create handler function, getHandler helps us to avoid
	// limitations to use fixture abject as closure member of handler function.
	getHandler := func(fixture HTTPFixture) func(w http.ResponseWriter, r *http.Request) {
		return func(w http.ResponseWriter, r *http.Request) {
			rdata, err := io.ReadAll(r.Body)
			if err != nil {
				t.Logf("method: %v, url: %v", r.Method, r.URL)
				t.Errorf("can't read request from the request (req ur): %v", err)
				return
			}

			if !bytes.Equal(fixture.Request, rdata) &&
				(fixture.Request != nil && string(rdata) != "null") {
				t.Logf("method: %v, url: %v", r.Method, r.URL)
				t.Errorf(
					"request not match: expected %v, got %v",
					string(fixture.Request),
					string(rdata),
				)
				return
			}
			w.WriteHeader(fixture.ResponseCode)
			if n, err := w.Write(fixture.Response); err != nil {
				t.Errorf("fail to write response: %v, written: %v", err, n)
				return
			}
		}
	}

	mux := http.NewServeMux()
	// handlersMap uses keys like <METHOD>:<URL> to bind handler fuctions to URLs with specific method
	// and use simple routing to match request to handler
	handlersMap := map[string]func(http.ResponseWriter, *http.Request){}
	for _, fixture := range playFixtures {
		handlerURI := fmt.Sprintf("%v:%v", fixture.Method, fixture.URL)
		handlersMap[handlerURI] = getHandler(fixture)
	}

	// root handler matches URL and http method with fixture handler and calls it
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		handlerURI := fmt.Sprintf("%v:%v", r.Method, r.URL.Path)
		handler, ok := handlersMap[handlerURI]
		if ok {
			handler(w, r)
			return
		}
		w.WriteHeader(http.StatusInternalServerError)
	})

	server := httptest.NewServer(mux)
	// after server is ready to accept connections, we run test itself
	testFunc(server)
	server.Close()
}
