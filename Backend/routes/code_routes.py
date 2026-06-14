"""Code <-> Flowchart endpoints."""
from flask import Blueprint, request, jsonify
from services.code_to_flowchart import code_to_mermaid
from services.gemini_service import flowchart_to_code
from services.jwt_service import auth_required
from models.session import save_session

code_bp = Blueprint("code", __name__)


@code_bp.post("/code-to-flowchart")
@auth_required
def code_to_flowchart_route():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    if not code.strip():
        return jsonify({"error": "Empty code"}), 400
    flowchart = code_to_mermaid(code, language)
    save_session(
        user_id=request.user_id, source_code=code, flowchart=flowchart,
        language=language, kind="code_to_flowchart",
    )
    return jsonify({"flowchart": flowchart})


@code_bp.post("/flowchart-to-code")
@auth_required
def flowchart_to_code_route():
    data = request.get_json(silent=True) or {}
    mermaid = data.get("flowchart", "")
    language = data.get("language", "python")
    if not mermaid.strip():
        return jsonify({"error": "Empty flowchart"}), 400
    try:
        code = flowchart_to_code(mermaid, language)
    except Exception as e:
        return jsonify({"error": str(e)}), 502
    save_session(
        user_id=request.user_id, source_code=code, flowchart=mermaid,
        language=language, kind="flowchart_to_code",
    )
    return jsonify({"code": code})
