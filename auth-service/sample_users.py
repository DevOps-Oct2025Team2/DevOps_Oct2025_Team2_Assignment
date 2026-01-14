import os
from werkzeug.security import generate_password_hash
from app import app
from db import db
from models import User

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

USER_USERNAME = os.getenv("USER_USERNAME", "user1")
USER_PASSWORD = os.getenv("USER_PASSWORD", "user123")

with app.app_context():
    if not User.query.filter_by(username=ADMIN_USERNAME).first():
        admin = User(
            username=ADMIN_USERNAME,
            password_hash=generate_password_hash(ADMIN_PASSWORD),
            role="admin"
        )
        db.session.add(admin)

    if not User.query.filter_by(username=USER_USERNAME).first():
        user = User(
            username=USER_USERNAME,
            password_hash=generate_password_hash(USER_PASSWORD),
            role="user"
        )
        db.session.add(user)

    db.session.commit()
    print("Sample user/s created successfully.")

