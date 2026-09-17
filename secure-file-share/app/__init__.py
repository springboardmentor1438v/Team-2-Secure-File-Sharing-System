from __future__ import annotations

from datetime import timedelta

from flask import Flask, jsonify, render_template, request

from .config import Config
from .db import close_db, init_db

CSP = (
    "default-src 'self'; "
    "img-src 'self' data:; "
    "style-src 'self'; "
    "script-src 'self'; "
    "object-src 'none'; "
    "base-uri 'none'; "
    "form-action 'self'; "
    "frame-ancestors 'none'"
)


def create_app(config_object: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
        seconds=config_object.PERMANENT_SESSION_LIFETIME
    )
    app.config["STORAGE_DIR"].mkdir(parents=True, exist_ok=True)
    init_db(app.config["DATABASE_PATH"])

    app.teardown_appcontext(close_db)

    from .views import auth, files, shares

    app.register_blueprint(auth.bp)
    app.register_blueprint(files.bp)
    app.register_blueprint(shares.bp)

    from .security import csrf_token, current_user

    @app.context_processor
    def inject_globals():
        return {"csrf_token": csrf_token, "user": current_user()}

    @app.after_request
    def harden(response):
        response.headers.setdefault("Content-Security-Policy", CSP)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        if app.config.get("SESSION_COOKIE_SECURE"):
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return response

    @app.errorhandler(404)
    def not_found(err):
        return _error(404, "That page or link does not exist.")

    @app.errorhandler(400)
    def bad_request(err):
        return _error(400, getattr(err, "description", "Bad request."))

    @app.errorhandler(403)
    def forbidden(err):
        return _error(403, "You do not have access to that.")

    @app.errorhandler(413)
    def too_large(err):
        limit = app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
        return _error(413, f"That file is over the {limit} MB upload limit.")

    @app.errorhandler(429)
    def too_many(err):
        return _error(429, getattr(err, "description", "Too many attempts. Wait a few minutes."))

    def _error(code: int, message: str):
        if request.path.startswith("/api/"):
            return jsonify(error=message), code
        return render_template("error.html", code=code, message=message), code

    return app
