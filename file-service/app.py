from flask import Flask
from flask_migrate import Migrate
from db import db
import models # ensure File model is registered

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://file_user:file_pass@localhost:5434/file_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

from routes import bp
app.register_blueprint(bp)

@app.get("/health")
def health():
    return {"status": "ok"}

