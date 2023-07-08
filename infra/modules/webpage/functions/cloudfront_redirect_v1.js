function handler(event) {
    var request = event.request;

    var paths = request.uri.split('/');
    var lastPath = paths[paths.length - 1];
    var isFile = lastPath.split('.').length > 1;
    if (!isFile) {
        request.uri = "/v1.0/index.html";
        request.querystring = {}
    }

    return request;
}