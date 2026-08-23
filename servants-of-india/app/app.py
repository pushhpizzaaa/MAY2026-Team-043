"""Flask application factory + entrypoint.

Run locally with:  python -m app.app
"""
import os

from flask import Flask, send_from_directory
from flask_cors import CORS

from .config import Config
from .extensions import db, jwt
from .utils.responses import ApiError, error


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Ensure local upload dir exists (used by the local storage backend).
    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    # --- Extensions ---
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}, r"/uploads/*": {"origins": "*"}})

    # --- Interactive API docs (Swagger UI at /api/docs) ---
    from .docs import init_swagger
    init_swagger(app)

    # --- Models must be imported so create_all sees them ---
    from . import models  # noqa: F401

    # --- Blueprints ---
    from .auth.routes import auth_bp
    from .users.routes import users_bp
    from .categories.routes import categories_bp
    from .events.routes import events_bp
    from .submissions.routes import submissions_bp
    from .reviews.routes import reviews_bp
    from .progress.routes import progress_bp
    from .certificates.routes import certificates_bp
    from .notifications.routes import notifications_bp
    from .admin.routes import admin_bp

    for bp in (
        auth_bp, users_bp, categories_bp, events_bp, submissions_bp, reviews_bp,
        progress_bp, certificates_bp, notifications_bp, admin_bp,
    ):
        app.register_blueprint(bp)

    # --- Local uploads static serving (local storage backend only) ---
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(app.config["UPLOAD_DIR"], filename)

    @app.route("/api/health")
    def health():
        return {"success": True, "data": {"status": "ok"}}

    # --- Error handlers ---
    @app.errorhandler(ApiError)
    def handle_api_error(err: ApiError):
        return error(err.message, err.status, err.details)

    @app.errorhandler(404)
    def handle_404(_):
        return error("Not found", 404)

    @app.errorhandler(413)
    def handle_too_large(_):
        return error("File too large (max 5 MB)", 413)

    @app.errorhandler(Exception)
    def handle_unexpected(err):  # pragma: no cover - safety net
        if isinstance(err, ApiError):
            return error(err.message, err.status, err.details)
        app.logger.exception("Unhandled error")
        return error("Internal server error", 500)

    # Create tables on boot (MVP convenience; no migrations).
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config["PORT"], debug=app.config["ENV"] == "development")
