package version

import (
	"fmt"
	"net/http"
)

var version = "0.0.0" // default version in case wasn't specified during build explicitly

// getVersionFiles returns current version.
//
// swagger:route GET /version reports Version.
//
// Get files returns list of demo files.
//
//	Consumes:
//	- application/json
//
//	Produces:
//	- application/json
//
//	Responses:
//	  200: Version
func GetVersionHandler(w http.ResponseWriter, _ *http.Request) {
	// for simplicity, we do not follow the domain driven design for now
	w.WriteHeader(http.StatusOK)
	// for simplicity, we calculate this each time we got called
	// since it shouldn't happen much (manual operation of human)
	fmt.Fprintf(w, `{"version": "%s"}`, version)
}

func GetVersion() string {
	return version
}
