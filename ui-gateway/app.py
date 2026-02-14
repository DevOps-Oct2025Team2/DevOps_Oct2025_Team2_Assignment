from flask import Flask, render_template, redirect, request, Response
from prometheus_flask_exporter import PrometheusMetrics
import requests
import os
from flask import jsonify

app = Flask(__name__)

# Prometheus metrics
metrics = PrometheusMetrics(app)
metrics.info("service_info", "UI Gateway service", service="ui-gateway")

AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL",
    "http://localhost:5000"  # safe local default
)
FILE_SERVICE_URL = os.getenv(
    "FILE_SERVICE_URL",
    "http://localhost:5002"  # safe local default
)

def _proxy_request(base_url, path):
    content_type = request.headers.get("Content-Type", "")
    is_multipart = content_type.startswith("multipart/form-data")
    is_json = "application/json" in content_type

    headers = {k: v for k, v in request.headers if k.lower() != "host"}
    params = request.args or None

    files = None
    data = None
    json_body = None

    if is_multipart:
        # Let requests set the multipart boundary and length
        headers.pop("Content-Type", None)
        headers.pop("Content-Length", None)
        files = {
            name: (fs.filename, fs.stream, fs.mimetype)
            for name, fs in request.files.items()
        }
        data = request.form
    elif is_json:
        json_body = request.get_json(silent=True)
    else:
        data = request.get_data() or None


    # SSRF Mitigation: Only allow certain path patterns (example: alphanumeric, dashes, slashes)
    import re
    if not re.match(r'^[\w\-/]+$', path):
        return {"error": "Invalid path."}, 400

    # Prevent open redirect/host injection by not allowing protocol or double slashes
    if '//' in path or path.startswith('http'):
        return {"error": "Invalid path."}, 400

    try:
        resp = requests.request(
            method=request.method,
            url=f"{base_url}/{path.lstrip('/')}" ,
            params=params,
            json=json_body,
            data=data,
            files=files,
            headers=headers,
            timeout=10
        )

        # XSS Mitigation: Do not reflect user input directly, and set content-type safely
        # Force JSON handling to prevent XSS
        try:
            return jsonify(resp.json()), resp.status_code
        except ValueError:
            # If not JSON, return as plain text safely
            return Response(
                resp.text,
                status=resp.status_code,
                content_type="text/plain; charset=utf-8"
            )

    except requests.RequestException as e:
        print("PROXY ERROR:", repr(e))
        return {"error": "Upstream service unavailable"}, 503

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/admin")
def admin_page():
    return render_template("admin.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/api/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_api(path):
    """
    Browser -> ui-gateway -> auth-service
    """
    return _proxy_request(f"{AUTH_SERVICE_URL}/api", path)

@app.route("/files/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_files(path):
    """
    Browser -> ui-gateway -> file-service
    """
    return _proxy_request(FILE_SERVICE_URL, path)

@app.get("/health")
def health():
    return {"status": "ok", "service": "ui-gateway"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
