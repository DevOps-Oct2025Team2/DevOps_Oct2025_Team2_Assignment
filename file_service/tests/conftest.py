import os
import pytest
from app import create_app
from db import db
import jwt
from datetime import datetime, timedelta, UTC
from pathlib import Path

@pytest.fixture(autouse=True)
def set_testing_env():
    os.environ["TESTING"] = "true"
    os.environ["JWT_SECRET"] = "test-secret"

def make_test_jwt(user_id=1, role="user"):
    payload = {
        "sub": str(user_id),  
        "role": role,
        "exp": datetime.now(UTC) + timedelta(minutes=5),
    }
    return jwt.encode(payload, "test-secret", algorithm="HS256")

@pytest.fixture(autouse=True)
def set_testing_env():
    os.environ["TESTING"] = "true"
    os.environ["JWT_SECRET"] = "test-secret"

@pytest.fixture
def app():
    app = create_app("sqlite:///:memory:")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
