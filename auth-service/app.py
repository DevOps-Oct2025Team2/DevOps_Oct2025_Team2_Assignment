import os
from dotenv import load_dotenv

# Load shared .env FIRST
load_dotenv()

# Set service identity (override shared .env)
os.environ.setdefault("SERVICE_NAME", "auth-service")
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from db import db
import models
from routes import auth_routes
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from datetime import datetime, timezone
from notify import notify_event
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

def _get_cors_origins():
    raw_origins = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

CORS(
    app,
    origins=_get_cors_origins(),
    allow_headers="*",
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    supports_credentials=False,
)

metrics = PrometheusMetrics(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(auth_routes, url_prefix="/api")

@app.errorhandler(Exception)
def handle_unhandled_exception(e):
    print("UNHANDLED ERROR:", repr(e))
    # Let Flask handle HTTP errors normally
    if isinstance(e, HTTPException):
        return e

    notify_event(
        event_type="server_error",
        dedupe_key=f"{request.method}:{request.path}:{request.remote_addr}",
        subject="Unhandled exception (500)",
        body=(
            f"ts={datetime.now(timezone.utc).isoformat()} "
            f"service={os.getenv('SERVICE_NAME')} "
            f"event=server_error status=500 "
            f"method={request.method} path={request.path} "
            f"ip={request.remote_addr} "
            f"error={type(e).__name__}"
        ),
    )

    return jsonify({"error": "Internal Server Error"}), 500

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)

