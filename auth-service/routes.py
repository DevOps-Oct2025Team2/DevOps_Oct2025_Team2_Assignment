# ===== Imports =====
from functools import wraps
import os
import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models import User

# Blueprint
auth_routes = Blueprint("auth_routes", __name__)

# JWT Configuration
PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY")
PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY")
JWT_EXPIRY_HOURS = 1

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
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    }

    token = jwt.encode(payload, PRIVATE_KEY, algorithm="ES256")

    return jsonify({
        "access_token": token,
        "token_type": "Bearer"
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
            decoded = jwt.decode(token, PUBLIC_KEY, algorithms=["ES256"])
            request.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

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


