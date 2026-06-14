"""Authentication endpoints."""
import re
from flask import Blueprint, request, jsonify
from models.user import (
    create_user, get_user_by_email, get_user_by_id, check_password,
)
from services.jwt_service import issue_token, auth_required

auth_bp = Blueprint("auth", __name__)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not (3 <= len(username) <= 80):
        return jsonify({"error": "Username must be 3-80 chars"}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Invalid email"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if get_user_by_email(email):
        return jsonify({"error": "Email already registered"}), 409

    try:
        uid = create_user(username, email, password)
    except Exception as e:
        return jsonify({"error": f"Could not create user: {e}"}), 500

    token = issue_token(uid, username)
    return jsonify({"token": token, "user": {"id": uid, "username": username, "email": email}})


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = get_user_by_email(email)
    if not user or not check_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid credentials"}), 401
    token = issue_token(user["id"], user["username"])
    return jsonify({
        "token": token,
        "user": {"id": user["id"], "username": user["username"], "email": user["email"]},
    })


@auth_bp.get("/me")
@auth_required
def me():
    user = get_user_by_id(request.user_id)
    if not user:
        return jsonify({"error": "Not found"}), 404
    user["created_at"] = user["created_at"].isoformat() if user.get("created_at") else None
    return jsonify(user)
