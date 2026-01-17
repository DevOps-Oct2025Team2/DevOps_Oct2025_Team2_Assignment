import os
from flask import Flask
from flask_migrate import Migrate
from db import db
import models
from routes import auth_routes
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://auth_user:auth_pass@localhost:5433/auth_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(auth_routes, url_prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)