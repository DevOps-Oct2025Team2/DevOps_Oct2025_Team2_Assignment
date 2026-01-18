# ===== Imports =====
from functools import wraps
import os
import jwt
from datetime import datetime, timedelta, UTC
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models import User
from pathlib import Path

# Blueprint
auth_routes = Blueprint("auth_routes", __name__)

# JWT Configuration (ES256)
BASE_DIR = Path(__file__).resolve().parent

JWT_EXPIRY_HOURS = 1

TESTING = os.getenv("TESTING") == "true"

if TESTING:
    # Unit tests: simple symmetric key
    JWT_ALGORITHM = "HS256"
    PRIVATE_KEY = os.getenv("JWT_SECRET", "test-secret")
    PUBLIC_KEY = PRIVATE_KEY
else:
    # Production / local dev: ES256 with PEM keys
    JWT_ALGORITHM = "ES256"

    PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY")
    PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY")

    if not PRIVATE_KEY or not PUBLIC_KEY:
        BASE_DIR = Path(__file__).resolve().parent
        with open(BASE_DIR / "ec_private.pem", "r") as f:
            PRIVATE_KEY = f.read()
        with open(BASE_DIR / "ec_public.pem", "r") as f:
            PUBLIC_KEY = f.read()

# LOGIN API (Authentication)
@auth_routes.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Invalid JSON body"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Missing credentials"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    payload = {
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.now(UTC) + timedelta(hours=JWT_EXPIRY_HOURS)
    }

    token = jwt.encode(payload, PRIVATE_KEY, algorithm=JWT_ALGORITHM)

    return jsonify({
        "access_token": token,
        "token_type": "Bearer",
        "role": user.role
    }), 200

# AUTH MIDDLEWARE
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Token missing or invalid"}), 401

        token = auth_header.split(" ")[1]

        try:
            decoded = jwt.decode(token, PUBLIC_KEY, algorithms=[JWT_ALGORITHM])
            request.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.user["role"] != "admin":
            return jsonify({"message": "Forbidden"}), 403
        return f(*args, **kwargs)

    return decorated

# PROTECTED ROUTE (AUTH CHECK)
@auth_routes.route("/profile", methods=["GET"])
@token_required
def profile():
    return jsonify({
        "message": "Authenticated access granted",
        "user": request.user
    }), 200


@auth_routes.route("/admin", methods=["GET"])
@token_required
@admin_required
def admin_dashboard():
    return jsonify({"message": "Admin access granted"}), 200

@auth_routes.post("/logout")
def logout():
    return jsonify({"message": "Logged out"}), 200
