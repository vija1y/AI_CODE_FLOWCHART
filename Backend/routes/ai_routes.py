"""Generative-AI endpoints (Gemini)."""
from flask import Blueprint, request, jsonify
from services.gemini_service import explain_code, summarize_code, suggest_improvements
from services.jwt_service import auth_required
from models.session import save_session

ai_bp = Blueprint("ai", __name__)


@ai_bp.post("/explain-code")
@auth_required
def explain():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    if not code.strip():
        return jsonify({"error": "Empty code"}), 400
    try:
        text = explain_code(code, language)
    except Exception as e:
        return jsonify({"error": str(e)}), 502
    save_session(
        user_id=request.user_id, source_code=code, explanation=text,
        language=language, kind="explain",
    )
    return jsonify({"explanation": text})


@ai_bp.post("/generate-summary")
@auth_required
def summary():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    if not code.strip():
        return jsonify({"error": "Empty code"}), 400
    try:
        text = summarize_code(code, language)
    except Exception as e:
        return jsonify({"error": str(e)}), 502
    return jsonify({"summary": text})


@ai_bp.post("/suggest-improvements")
@auth_required
def improvements():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    if not code.strip():
        return jsonify({"error": "Empty code"}), 400
    try:
        text = suggest_improvements(code, language)
    except Exception as e:
        return jsonify({"error": str(e)}), 502
    return jsonify({"suggestions": text})
