"""
AI-Enhanced Code & Flowchart Learning System
Main Flask application entry point.
"""
import os
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv

from database.db import init_db
from routes.auth_routes import auth_bp
from routes.code_routes import code_bp
from routes.ml_routes import ml_bp
from routes.ai_routes import ai_bp
from routes.history_routes import history_bp

load_dotenv()


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")
    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", "jwt-change-me")
    app.config["JWT_EXP_HOURS"] = int(os.getenv("JWT_EXP_HOURS", "24"))

    CORS(app, supports_credentials=True)
    init_db(app)

    # API blueprints
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(code_bp, url_prefix="/api")
    app.register_blueprint(ml_bp, url_prefix="/api")
    app.register_blueprint(ai_bp, url_prefix="/api")
    app.register_blueprint(history_bp, url_prefix="/api")

    # Page routes (server-rendered shells; logic in JS)
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/register")
    def register_page():
        return render_template("register.html")

    @app.route("/dashboard")
    def dashboard_page():
        return render_template("dashboard.html")

    @app.route("/editor")
    def editor_page():
        return render_template("editor.html")

    @app.route("/flowchart-to-code")
    def f2c_page():
        return render_template("flowchart_to_code.html")

    @app.route("/history")
    def history_page():
        return render_template("history.html")

    @app.route("/profile")
    def profile_page():
        return render_template("profile.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
