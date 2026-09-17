from __future__ import annotations

from datetime import datetime, timezone

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, session, url_for)

from ..db import get_db
from ..security import (audit, hash_token, rate_limit, require_csrf,
                        utcnow_iso, verify_password)
from .files import _stream_response

bp = Blueprint("shares", __name__)


@bp.before_request
def csrf_guard():
    require_csrf()


def _lookup(token: str):
    """Resolve a raw token to a live share, or None."""
    row = get_db().execute(
        """SELECT s.*, f.display_name, f.size_bytes, f.content_type, f.sha256,
                  f.blob_name, f.wrapped_key
             FROM shares s JOIN files f ON f.id = s.file_id
            WHERE s.token_hash = ?""",
        (hash_token(token),),
    ).fetchone()
    if row is None or row["revoked"]:
        return None
    if datetime.fromisoformat(row["expires_at"]) <= datetime.now(timezone.utc):
        return None
    if row["max_downloads"] is not None and row["download_count"] >= row["max_downloads"]:
        return None
    return row


def _unlocked(share_id: int) -> bool:
    return share_id in session.get("unlocked", [])


@bp.get("/d/<token>")
def open_link(token: str):
    share = _lookup(token)
    if share is None:
        return render_template("expired.html"), 404

    needs_password = share["password_hash"] is not None
    return render_template(
        "share.html",
        share=share,
        token=token,
        needs_password=needs_password and not _unlocked(share["id"]),
        remaining=(
            None if share["max_downloads"] is None
            else share["max_downloads"] - share["download_count"]
        ),
    )


@bp.post("/d/<token>/unlock")
def unlock(token: str):
    limit, window = current_app.config["UNLOCK_RATE_LIMIT"]
    if not rate_limit("unlock", limit, window):
        abort(429, description="Too many password attempts on this link.")

    share = _lookup(token)
    if share is None:
        return render_template("expired.html"), 404

    if verify_password(share["password_hash"], request.form.get("password", "")):
        session["unlocked"] = list({*session.get("unlocked", []), share["id"]})
        return redirect(url_for("shares.download", token=token))

    audit("link.unlock_failed", target=share["display_name"])
    flash("That password is not right.", "error")
    return redirect(url_for("shares.open_link", token=token))


@bp.get("/d/<token>/file")
def download(token: str):
    share = _lookup(token)
    if share is None:
        return render_template("expired.html"), 404
    if share["password_hash"] is not None and not _unlocked(share["id"]):
        return redirect(url_for("shares.open_link", token=token))

    db = get_db()
    # Conditional update keeps the download cap correct under concurrency.
    cur = db.execute(
        """UPDATE shares SET download_count = download_count + 1
            WHERE id = ? AND revoked = 0
              AND (max_downloads IS NULL OR download_count < max_downloads)""",
        (share["id"],),
    )
    db.commit()
    if cur.rowcount != 1:
        return render_template("expired.html"), 404

    audit("link.downloaded", target=share["display_name"],
          detail=f"token {share['token_hint']}…")
    return _stream_response(share)
