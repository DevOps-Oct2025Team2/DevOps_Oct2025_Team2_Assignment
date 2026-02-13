import os
import logging
import sys
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

    def configure_logging(app: Flask):
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)sZ | %(levelname)s | %(name)s | service=%(service)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(formatter)

        # Replace default handlers so format is consistent
        app.logger.handlers.clear()
        app.logger.propagate = False
        app.logger.addHandler(handler)
        app.logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

        # Add a default field into log records
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.service = os.getenv("SERVICE_NAME", "file-service")
            return record

        logging.setLogRecordFactory(record_factory)

    configure_logging(app)
    
    app.config["ENABLE_METRICS"] = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    app.logger.info("logging_ready | enable_metrics=%s", app.config.get("ENABLE_METRICS"))

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

    app.config["UPLOAD_DIR"] = os.getenv("UPLOAD_DIR", "uploads")
    app.config["MAX_UPLOAD_SIZE_BYTES"] = 5 * 1024 * 1024
    app.config["ALLOWED_CONTENT_TYPES"] = {"text/plain", "image/png"}

    db.init_app(app)
    Migrate(app, db)

    from routes import bp
    app.register_blueprint(bp)

    def _sanitize_for_log(value):
        """
        Basic log injection mitigation:
        - convert to string
        - remove CR/LF to prevent log forging
        """
        if value is None:
            return "-"
        text = str(value)
        return text.replace("\r", "").replace("\n", "")

    @app.before_request
    def _log_request():
        method = _sanitize_for_log(request.method)
        path = _sanitize_for_log(request.path)
        ip = _sanitize_for_log(request.remote_addr)
        ua = _sanitize_for_log(request.headers.get("User-Agent", "-"))

        app.logger.info(
            "request | method=%s path=%s ip=%s ua=%s",
            method,
            path,
            ip,
            ua,
        )

    @app.after_request
    def _log_response(resp):
        method = _sanitize_for_log(request.method)
        path = _sanitize_for_log(request.path)

        app.logger.info(
            "response | method=%s path=%s status=%s",
            method,
            path,
            resp.status_code,
        )
        return resp

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        if isinstance(e, HTTPException):
            return e

        method = _sanitize_for_log(request.method)
        path = _sanitize_for_log(request.path)
        ip = _sanitize_for_log(request.remote_addr)

        app.logger.exception("unhandled_exception | method=%s path=%s", method, path)

        notify_event(
            event_type="server_error",
            dedupe_key=f"{method}:{path}:{ip}",
            subject="Unhandled exception (500)",
            body=(
                f"ts={datetime.now(timezone.utc).isoformat()} "
                f"service={os.getenv('SERVICE_NAME','file-service')} "
                f"event=server_error status=500 "
                f"method={method} path={path} "
                f"ip={ip} "
                f"error={type(e).__name__}"
            ),
        )

        return jsonify({"error": "Internal Server Error"}), 500

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app

app = create_app() if os.getenv("DATABASE_URL") else None

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5002)
