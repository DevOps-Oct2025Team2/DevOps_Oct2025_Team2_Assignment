# ===== Imports =====
from functools import wraps
import os
import jwt
from datetime import datetime, timedelta, UTC
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from db import db
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

@auth_routes.route("/admin/users", methods=["GET"])
@token_required
@admin_required
def get_all_users():
    users = User.query.all()

    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "created_at": u.created_at.isoformat()
        }
        for u in users
    ]), 200

@auth_routes.route("/admin/users", methods=["POST"])
@token_required
@admin_required
def create_user():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Invalid JSON body"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    # Prevent duplicate usernames
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    new_user = User(
        username=username,
        password_hash=generate_password_hash(password),
        role="user"  # FIXED ROLE
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@auth_routes.route("/admin/users/<int:user_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Prevent admin from deleting themselves
    if user.id == request.user["user_id"]:
        return jsonify({"message": "Cannot delete your own account"}), 403

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200
