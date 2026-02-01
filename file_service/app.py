from flask import Flask
from flask_migrate import Migrate
from db import db
from flask_cors import CORS
import models

def create_app(database_uri=None):
    app = Flask(__name__)
    CORS(
        app,
        origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_headers="*",
        expose_headers=["Content-Disposition"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        supports_credentials=False,
    )

    if database_uri is None:
        database_uri = "postgresql+psycopg2://file_user:file_pass@localhost:5434/file_db"

    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True

    app.config["UPLOAD_DIR"] = "uploads"
    app.config["MAX_UPLOAD_SIZE_BYTES"] = 5 * 1024 * 1024
    app.config["ALLOWED_CONENT_TYPES"] = {"text/plain", "image/png"}

    db.init_app(app)
    Migrate(app, db)

    from routes import bp
    app.register_blueprint(bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002) 
