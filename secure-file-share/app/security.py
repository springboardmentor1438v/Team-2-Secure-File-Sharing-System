from __future__ import annotations

import functools
import hashlib
import hmac
import re
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Deque

from flask import abort, current_app, g, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s.]+\.[^@\s]+$")


# --------------------------------------------------------------------------
# passwords
# --------------------------------------------------------------------------
def hash_password(password: str) -> str:
    return generate_password_hash(password, method="scrypt")


def verify_password(stored_hash: str | None, password: str) -> bool:
    if not stored_hash:
        return False
    return check_password_hash(stored_hash, password)


def password_problem(password: str) -> str | None:
    minimum = current_app.config["MIN_PASSWORD_LENGTH"]
    if len(password) < minimum:
        return f"Use at least {minimum} characters."
    if password.isdigit() or password.isalpha():
        return "Mix letters with numbers or symbols."
    return None


# --------------------------------------------------------------------------
# tokens
# --------------------------------------------------------------------------
def new_share_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Share tokens are stored hashed, so a database leak does not hand an
    attacker a set of working download links."""
    return hashlib.sha256(token.encode()).hexdigest()


# --------------------------------------------------------------------------
# CSRF
# --------------------------------------------------------------------------
def csrf_token() -> str:
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def require_csrf() -> None:
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return
    sent = request.form.get("csrf_token", "")
    expected = session.get("csrf", "")
    if not expected or not hmac.compare_digest(sent, expected):
        abort(400, description="Session expired. Reload the page and try again.")


# --------------------------------------------------------------------------
# rate limiting (in-process; swap for Redis when running multiple workers)
# --------------------------------------------------------------------------
_buckets: dict[str, Deque[float]] = defaultdict(deque)


def rate_limit(bucket: str, limit: int, window: int) -> bool:
    """Return True when the call is allowed."""
    key = f"{bucket}:{client_ip()}"
    now = time.time()
    hits = _buckets[key]
    while hits and now - hits[0] > window:
        hits.popleft()
    if len(hits) >= limit:
        return False
    hits.append(now)
    return True


def client_ip() -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded and current_app.config.get("TRUST_PROXY"):
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


# --------------------------------------------------------------------------
# session / current user
# --------------------------------------------------------------------------
def current_user():
    if "user" in g:
        return g.user
    uid = session.get("uid")
    g.user = None
    if uid:
        row = get_db().execute(
            "SELECT id, email, created_at FROM users WHERE id = ? AND is_active = 1",
            (uid,),
        ).fetchone()
        g.user = row
    return g.user


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


# --------------------------------------------------------------------------
# audit trail
# --------------------------------------------------------------------------
def audit(action: str, target: str | None = None, detail: str | None = None) -> None:
    user = current_user()
    actor = user["email"] if user else "anonymous"
    get_db().execute(
        "INSERT INTO audit_log (at, actor, action, target, ip, detail) VALUES (?,?,?,?,?,?)",
        (utcnow_iso(), actor, action, target, client_ip(), detail),
    )
    get_db().commit()


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
