"""Machine-learning logic-classification endpoint."""
from flask import Blueprint, request, jsonify
from services.ml_service import classify_code
from services.jwt_service import auth_required
from models.session import save_session

ml_bp = Blueprint("ml", __name__)


@ml_bp.post("/classify-logic")
@auth_required
def classify_logic():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    if not code.strip():
        return jsonify({"error": "Empty code"}), 400
    try:
        result = classify_code(code)
    except FileNotFoundError:
        return jsonify({"error": "Model not trained. Run ML/train_model.py"}), 500
    save_session(
        user_id=request.user_id, source_code=code,
        logic_type=result["logic_type"], confidence=result["confidence"],
        language=language, kind="classify",
    )
    return jsonify(result)
