from __future__ import annotations

import mimetypes
from datetime import datetime, timedelta, timezone

from flask import (Blueprint, Response, abort, current_app, flash, redirect,
                   render_template, request, url_for)
from werkzeug.utils import secure_filename

from .. import storage
from ..config import Config
from ..db import get_db
from ..security import (audit, current_user, hash_token, login_required,
                        new_share_token, require_csrf, utcnow_iso)

bp = Blueprint("files", __name__)


@bp.before_request
def csrf_guard():
    require_csrf()


@bp.get("/")
def home():
    if current_user():
        return redirect(url_for("files.dashboard"))
    return redirect(url_for("auth.login"))


@bp.get("/files")
@login_required
def dashboard():
    user = current_user()
    rows = get_db().execute(
        """
        SELECT f.*,
               (SELECT COUNT(*) FROM shares s
                 WHERE s.file_id = f.id AND s.revoked = 0
                   AND s.expires_at > ?) AS active_links
        FROM files f
        WHERE f.owner_id = ?
        ORDER BY f.created_at DESC
        """,
        (utcnow_iso(), user["id"]),
    ).fetchall()
    return render_template("dashboard.html", files=rows)


@bp.post("/files")
@login_required
def upload():
    user = current_user()
    upload = request.files.get("file")
    if not upload or not upload.filename:
        flash("Choose a file to upload.", "error")
        return redirect(url_for("files.dashboard"))

    name = secure_filename(upload.filename) or "untitled"
    content_type = (
        mimetypes.guess_type(name)[0] or "application/octet-stream"
    )

    meta = storage.store(
        upload.stream,
        current_app.config["STORAGE_DIR"],
        Config.master_key(),
    )
    if meta["size_bytes"] == 0:
        storage.delete(meta["blob_name"], current_app.config["STORAGE_DIR"])
        flash("That file is empty.", "error")
        return redirect(url_for("files.dashboard"))

    db = get_db()
    db.execute(
        """INSERT INTO files
           (owner_id, display_name, content_type, size_bytes, sha256,
            blob_name, wrapped_key, created_at)
           VALUES (?,?,?,?,?,?,?,?)""",
        (user["id"], name, content_type, meta["size_bytes"], meta["sha256"],
         meta["blob_name"], meta["wrapped_key"], utcnow_iso()),
    )
    db.commit()
    audit("file.uploaded", target=name, detail=f"{meta['size_bytes']} bytes")
    flash(f"Uploaded {name}.", "ok")
    return redirect(url_for("files.dashboard"))


def _owned_file(file_id: int):
    user = current_user()
    row = get_db().execute(
        "SELECT * FROM files WHERE id = ? AND owner_id = ?", (file_id, user["id"])
    ).fetchone()
    if row is None:
        abort(404)
    return row


@bp.get("/files/<int:file_id>/download")
@login_required
def download(file_id: int):
    row = _owned_file(file_id)
    audit("file.downloaded", target=row["display_name"], detail="owner")
    return _stream_response(row)


def _stream_response(row) -> Response:
    chunks = storage.read(
        row["blob_name"],
        row["wrapped_key"],
        current_app.config["STORAGE_DIR"],
        Config.master_key(),
    )
    response = Response(chunks, mimetype="application/octet-stream")
    filename = row["display_name"].replace('"', "")
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.headers["Content-Length"] = str(row["size_bytes"])
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@bp.get("/files/<int:file_id>")
@login_required
def detail(file_id: int):
    row = _owned_file(file_id)
    links = get_db().execute(
        "SELECT * FROM shares WHERE file_id = ? ORDER BY created_at DESC", (file_id,)
    ).fetchall()
    return render_template(
        "detail.html",
        file=row,
        links=links,
        now=utcnow_iso(),
        default_ttl=current_app.config["DEFAULT_LINK_TTL_HOURS"],
        max_ttl=current_app.config["MAX_LINK_TTL_HOURS"],
    )


@bp.post("/files/<int:file_id>/delete")
@login_required
def delete(file_id: int):
    row = _owned_file(file_id)
    db = get_db()
    db.execute("DELETE FROM files WHERE id = ?", (file_id,))
    db.commit()
    storage.delete(row["blob_name"], current_app.config["STORAGE_DIR"])
    audit("file.deleted", target=row["display_name"])
    flash(f"Deleted {row['display_name']} and every link to it.", "ok")
    return redirect(url_for("files.dashboard"))


@bp.post("/files/<int:file_id>/links")
@login_required
def create_link(file_id: int):
    row = _owned_file(file_id)
    user = current_user()

    try:
        hours = int(request.form.get("ttl_hours", current_app.config["DEFAULT_LINK_TTL_HOURS"]))
    except ValueError:
        hours = current_app.config["DEFAULT_LINK_TTL_HOURS"]
    hours = max(1, min(hours, current_app.config["MAX_LINK_TTL_HOURS"]))

    max_downloads = request.form.get("max_downloads", "").strip()
    limit = None
    if max_downloads:
        try:
            limit = max(1, min(int(max_downloads), 10_000))
        except ValueError:
            limit = None

    password = request.form.get("link_password", "")
    from ..security import hash_password

    token = new_share_token()
    expires = datetime.now(timezone.utc) + timedelta(hours=hours)

    db = get_db()
    db.execute(
        """INSERT INTO shares
           (file_id, created_by, token_hash, token_hint, password_hash,
            expires_at, max_downloads, created_at)
           VALUES (?,?,?,?,?,?,?,?)""",
        (file_id, user["id"], hash_token(token), token[:6],
         hash_password(password) if password else None,
         expires.isoformat(timespec="seconds"), limit, utcnow_iso()),
    )
    db.commit()
    audit("link.created", target=row["display_name"],
          detail=f"expires {expires.isoformat(timespec='minutes')}")

    link = url_for("shares.open_link", token=token, _external=True)
    return render_template("link_created.html", file=row, link=link,
                           expires=expires, limit=limit,
                           protected=bool(password))


@bp.post("/links/<int:share_id>/revoke")
@login_required
def revoke_link(share_id: int):
    user = current_user()
    db = get_db()
    row = db.execute(
        "SELECT s.*, f.display_name FROM shares s JOIN files f ON f.id = s.file_id "
        "WHERE s.id = ? AND s.created_by = ?",
        (share_id, user["id"]),
    ).fetchone()
    if row is None:
        abort(404)
    db.execute("UPDATE shares SET revoked = 1 WHERE id = ?", (share_id,))
    db.commit()
    audit("link.revoked", target=row["display_name"], detail=row["token_hint"] + "…")
    flash("Link revoked. Anyone holding it now gets a dead page.", "ok")
    return redirect(url_for("files.detail", file_id=row["file_id"]))


@bp.get("/activity")
@login_required
def activity():
    user = current_user()
    rows = get_db().execute(
        """SELECT * FROM audit_log
           WHERE actor = ?
              OR (actor = 'anonymous'
                  AND target IN (SELECT display_name FROM files WHERE owner_id = ?))
           ORDER BY id DESC LIMIT 200""",
        (user["email"], user["id"]),
    ).fetchall()
    return render_template("activity.html", events=rows)
