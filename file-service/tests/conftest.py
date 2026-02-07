import os
import pytest
from app import create_app
from db import db
import jwt
from datetime import datetime, timedelta, UTC
from pathlib import Path

@pytest.fixture(autouse=True)
def set_testing_env(monkeypatch):
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("JWT_SECRET", "test-secret")

    # runtime emails OFF by default in tests
    monkeypatch.setenv("ENABLE_RUNTIME_EMAILS", "false")

def make_test_jwt(user_id=1, role="user"):
    payload = {
        "sub": str(user_id),  
        "role": role,
        "exp": datetime.now(UTC) + timedelta(minutes=5),
    }
    return jwt.encode(payload, "test-secret", algorithm="HS256")

@pytest.fixture
def app():
    app = create_app("sqlite:///:memory:")
    app.config["TESTING"] = True 
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
