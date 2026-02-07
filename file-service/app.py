import os
from dotenv import load_dotenv

# Load shared .env FIRST
load_dotenv()

# Set service identity for this service
os.environ.setdefault("SERVICE_NAME", "file-service")
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from db import db
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
import models
from notify import notify_event
from werkzeug.exceptions import HTTPException
from datetime import datetime, timezone

def create_app(database_uri=None):
    app = Flask(__name__)

    app.config["ENABLE_METRICS"] = os.getenv("ENABLE_METRICS", "true").lower() == "true"

    if app.config["ENABLE_METRICS"]:
        metrics = PrometheusMetrics(app)
        
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
        expose_headers=["Content-Disposition"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        supports_credentials=False,
    )

    if database_uri is None:
        database_uri = os.getenv("DATABASE_URL")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = False

    app.config["UPLOAD_DIR"] = "uploads"
    app.config["MAX_UPLOAD_SIZE_BYTES"] = 5 * 1024 * 1024
    app.config["ALLOWED_CONTENT_TYPES"] = {"text/plain", "image/png"}

    db.init_app(app)
    Migrate(app, db)

    from routes import bp
    app.register_blueprint(bp)

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        # Let Flask handle normal HTTP errors (404, 401 etc.) normally
        if isinstance(e, HTTPException):
            return e

        # Send ONE alert email for unexpected server errors
        notify_event(
            event_type="server_error",
            dedupe_key=f"{request.method}:{request.path}:{request.remote_addr}",
            subject="Unhandled exception (500)",
            body=(
                f"ts={datetime.now(timezone.utc).isoformat()} "
                f"service={os.getenv('SERVICE_NAME','file-service')} "
                f"event=server_error status=500 "
                f"method={request.method} path={request.path} "
                f"ip={request.remote_addr} "
                f"error={type(e).__name__}"
            ),
        )
        # Return safe response to client
        return jsonify({"error": "Internal Server Error"}), 500

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app

app = create_app() if os.getenv("DATABASE_URL") else None

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5002)
