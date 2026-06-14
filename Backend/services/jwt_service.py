"""JWT issue + verify + auth decorator."""
import os
import datetime as dt
from functools import wraps
import jwt
from flask import request, jsonify, current_app


def issue_token(user_id: int, username: str) -> str:
    payload = {
        "uid": user_id,
        "username": username,
        "exp": dt.datetime.utcnow() + dt.timedelta(
            hours=int(os.getenv("JWT_EXP_HOURS", "24"))
        ),
        "iat": dt.datetime.utcnow(),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")


def decode_token(token: str):
    return jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth.split(" ", 1)[1].strip()
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        request.user_id = payload["uid"]
        request.username = payload.get("username")
        return fn(*args, **kwargs)
    return wrapper
