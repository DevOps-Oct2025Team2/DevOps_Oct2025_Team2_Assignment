import os
import pytest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
## For unit testing and CI
os.environ["JWT_PRIVATE_KEY"] = "test-private-key"
os.environ["JWT_PUBLIC_KEY"] = "test-public-key"
os.environ["TESTING"] = "true"
os.environ["JWT_SECRET"] = "unit-test-secret"

from app import app
from db import db
from models import User
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_user():
    with app.app_context():
        admin = User(
            username="admin",
            password_hash=generate_password_hash("admin123"),
            role="admin"
        )

        user = User(
            username="user1",
            password_hash=generate_password_hash("user123"),
            role="user"
        )

        db.session.add_all([admin, user])
        db.session.commit()

        return admin

