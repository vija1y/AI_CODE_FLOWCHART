"""Learning-session history endpoints."""
from flask import Blueprint, request, jsonify
from services.jwt_service import auth_required
from models.session import list_sessions, delete_session

history_bp = Blueprint("history", __name__)


@history_bp.get("/history")
@auth_required
def history():
    rows = list_sessions(request.user_id)
    for r in rows:
        if r.get("created_at"):
            r["created_at"] = r["created_at"].isoformat()
    return jsonify({"sessions": rows})


@history_bp.delete("/history/<int:sid>")
@auth_required
def delete(sid):
    n = delete_session(request.user_id, sid)
    if not n:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"deleted": sid})
