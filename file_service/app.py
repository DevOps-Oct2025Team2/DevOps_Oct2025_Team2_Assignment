from flask import Flask
from flask_migrate import Migrate
from db import db
import models

def create_app(database_uri=None):
    app = Flask(__name__)

    if database_uri is None:
        database_uri = "postgresql+psycopg2://file_user:file_pass@localhost:5434/file_db"

    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True

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
    app.run(host="0.0.0.0", port=5000, debug=True)