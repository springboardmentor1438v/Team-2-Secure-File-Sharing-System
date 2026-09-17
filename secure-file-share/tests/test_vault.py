"""Run with:  python -m pytest -q  (from the project root)"""

from __future__ import annotations

import base64
import io
import os
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402
from app import crypto  # noqa: E402
from app.config import Config  # noqa: E402

EMAIL = "dana@example.com"
PASSWORD = "correct-horse-battery-staple"


@pytest.fixture()
def app(tmp_path, monkeypatch):
    key = base64.urlsafe_b64encode(os.urandom(32)).decode()
    monkeypatch.setattr(Config, "MASTER_KEY_B64", key)
    monkeypatch.setattr(Config, "STORAGE_DIR", tmp_path / "blobs")
    monkeypatch.setattr(Config, "DATABASE_PATH", tmp_path / "vault.db")
    monkeypatch.setattr(Config, "SECRET_KEY", "test-secret")
    application = create_app(Config)
    application.config["TESTING"] = True
    return application


@pytest.fixture()
def client(app):
    return app.test_client()


def csrf(client, path="/login"):
    page = client.get(path).get_data(as_text=True)
    match = re.search(r'name="csrf_token" value="([^"]+)"', page)
    assert match, "no csrf token on page"
    return match.group(1)


def register(client):
    token = csrf(client, "/register")
    return client.post(
        "/register",
        data={"csrf_token": token, "email": EMAIL, "password": PASSWORD},
        follow_redirects=True,
    )


def upload(client, name="report.txt", body=b"top secret quarterly numbers"):
    token = csrf(client, "/files")
    return client.post(
        "/files",
        data={"csrf_token": token, "file": (io.BytesIO(body), name)},
        content_type="multipart/form-data",
        follow_redirects=True,
    )


def make_link(client, file_id=1, **extra):
    token = csrf(client, f"/files/{file_id}")
    data = {"csrf_token": token, "ttl_hours": "24", **extra}
    page = client.post(f"/files/{file_id}/links", data=data).get_data(as_text=True)
    match = re.search(r"http://[^<\s]+/d/([A-Za-z0-9_-]+)", page)
    assert match, "no share link returned"
    return match.group(1)


# --- crypto ---------------------------------------------------------------
def test_roundtrip_multi_chunk():
    plaintext = os.urandom(crypto.CHUNK_SIZE * 3 + 17)
    dek = crypto.generate_key()
    out = io.BytesIO()
    size = crypto.encrypt_stream(io.BytesIO(plaintext), out, dek)
    assert size == len(plaintext)
    out.seek(0)
    assert b"".join(crypto.decrypt_stream(out, dek)) == plaintext


def test_ciphertext_does_not_contain_plaintext():
    plaintext = b"the eagle lands at midnight" * 100
    out = io.BytesIO()
    crypto.encrypt_stream(io.BytesIO(plaintext), out, crypto.generate_key())
    assert b"eagle" not in out.getvalue()


def test_tampering_is_detected():
    dek = crypto.generate_key()
    out = io.BytesIO()
    crypto.encrypt_stream(io.BytesIO(b"hello" * 50), out, dek)
    blob = bytearray(out.getvalue())
    blob[-5] ^= 0x01
    with pytest.raises(crypto.DecryptionError):
        list(crypto.decrypt_stream(io.BytesIO(bytes(blob)), dek))


def test_truncation_is_detected():
    dek = crypto.generate_key()
    out = io.BytesIO()
    crypto.encrypt_stream(io.BytesIO(os.urandom(crypto.CHUNK_SIZE * 2)), out, dek)
    blob = out.getvalue()
    head = blob[: 13 + 4 + crypto.CHUNK_SIZE + 16]  # header + first chunk only
    with pytest.raises(crypto.DecryptionError):
        list(crypto.decrypt_stream(io.BytesIO(head), dek))


def test_wrong_master_key_cannot_unwrap():
    dek = crypto.generate_key()
    wrapped = crypto.wrap_key(dek, os.urandom(32))
    with pytest.raises(crypto.DecryptionError):
        crypto.unwrap_key(wrapped, os.urandom(32))


# --- auth -----------------------------------------------------------------
def test_dashboard_requires_sign_in(client):
    assert client.get("/files").status_code == 302


def test_register_then_upload_and_download(client, app):
    register(client)
    upload(client)
    assert b"report.txt" in client.get("/files").data

    body = client.get("/files/1/download").data
    assert body == b"top secret quarterly numbers"

    # the bytes on disk are not the bytes we uploaded
    blobs = list(Path(app.config["STORAGE_DIR"]).rglob("*.enc"))
    assert len(blobs) == 1
    assert b"quarterly" not in blobs[0].read_bytes()


def test_weak_password_rejected(client):
    token = csrf(client, "/register")
    page = client.post(
        "/register",
        data={"csrf_token": token, "email": "x@example.com", "password": "short"},
        follow_redirects=True,
    ).get_data(as_text=True)
    assert "at least 12 characters" in page


def test_post_without_csrf_is_rejected(client):
    assert client.post("/register", data={"email": EMAIL, "password": PASSWORD}).status_code == 400


def test_other_users_files_are_invisible(client, app):
    register(client)
    upload(client)
    client.post("/logout", data={"csrf_token": csrf(client, "/files")})

    other = app.test_client()
    token = csrf(other, "/register")
    other.post("/register", data={"csrf_token": token, "email": "mal@example.com",
                                  "password": PASSWORD}, follow_redirects=True)
    assert other.get("/files/1/download").status_code == 404


# --- sharing --------------------------------------------------------------
def test_share_link_is_downloadable_by_anyone(client, app):
    register(client)
    upload(client)
    token = make_link(client)

    anon = app.test_client()
    assert b"report.txt" in anon.get(f"/d/{token}").data
    assert anon.get(f"/d/{token}/file").data == b"top secret quarterly numbers"


def test_download_limit_is_enforced(client, app):
    register(client)
    upload(client)
    token = make_link(client, max_downloads="1")

    anon = app.test_client()
    assert anon.get(f"/d/{token}/file").status_code == 200
    assert anon.get(f"/d/{token}/file").status_code == 404


def test_password_protected_link(client, app):
    register(client)
    upload(client)
    token = make_link(client, link_password="letmein-please-42")

    anon = app.test_client()
    page = anon.get(f"/d/{token}").get_data(as_text=True)
    assert "password protected" in page
    # without unlocking, the download bounces back to the unlock page
    assert anon.get(f"/d/{token}/file").status_code == 302

    csrf_value = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)
    anon.post(f"/d/{token}/unlock", data={"csrf_token": csrf_value,
                                          "password": "letmein-please-42"})
    assert anon.get(f"/d/{token}/file").data == b"top secret quarterly numbers"


def test_revoked_link_stops_working(client, app):
    register(client)
    upload(client)
    token = make_link(client)
    client.post("/links/1/revoke", data={"csrf_token": csrf(client, "/files/1")})

    anon = app.test_client()
    assert anon.get(f"/d/{token}/file").status_code == 404


def test_expired_link_stops_working(client, app):
    register(client)
    upload(client)
    token = make_link(client)
    with app.app_context():
        from app.db import get_db
        db = get_db()
        db.execute("UPDATE shares SET expires_at = '2020-01-01T00:00:00+00:00'")
        db.commit()

    anon = app.test_client()
    assert anon.get(f"/d/{token}").status_code == 404


def test_unknown_token_is_not_found(client, app):
    register(client)
    upload(client)
    make_link(client)
    assert app.test_client().get("/d/" + "A" * 43).status_code == 404


def test_deleting_a_file_removes_the_blob(client, app):
    register(client)
    upload(client)
    token = make_link(client)
    client.post("/files/1/delete", data={"csrf_token": csrf(client, "/files/1")})

    assert not list(Path(app.config["STORAGE_DIR"]).rglob("*.enc"))
    assert app.test_client().get(f"/d/{token}/file").status_code == 404


def test_activity_log_records_downloads(client, app):
    register(client)
    upload(client)
    token = make_link(client)
    app.test_client().get(f"/d/{token}/file")
    page = client.get("/activity").get_data(as_text=True)
    assert "link.downloaded" in page and "file.uploaded" in page


def test_security_headers_present(client):
    headers = client.get("/login").headers
    assert "default-src 'self'" in headers["Content-Security-Policy"]
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
