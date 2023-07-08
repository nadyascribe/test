# Test Tools Package
Please use this package to store common testing code.
Check this package please before you will try reinvent the wheel :)

## Logger
Main binary global contains logger initialization, and to avoid copy this code
in each test, please use [InitLogger](./logger.go) from this package.

## References
Test mocks and fixtures often contains constant values references, please
use [RefInt, RefStr etc.](./var_refs.go) to make variable references for constant values.

## Mock HTTP Requests
To mock external API calls by overriding HTTP client, and use fixtures for the requests and
responses you can use [WithMockedHTTPServer](./http_mock_server.go) function, which can replay
fixtures as request/response pairs. This methods compares request bodies with fixture body
and fails if they not match.
