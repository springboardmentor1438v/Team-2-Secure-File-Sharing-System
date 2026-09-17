from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    created_at    TEXT    NOT NULL,
    is_active     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS files (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    display_name   TEXT    NOT NULL,
    content_type   TEXT    NOT NULL,
    size_bytes     INTEGER NOT NULL,
    sha256         TEXT    NOT NULL,
    blob_name      TEXT    NOT NULL UNIQUE,
    wrapped_key    BLOB    NOT NULL,
    created_at     TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_files_owner ON files(owner_id);

CREATE TABLE IF NOT EXISTS shares (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id        INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    created_by     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash     TEXT    NOT NULL UNIQUE,
    token_hint     TEXT    NOT NULL,
    password_hash  TEXT,
    expires_at     TEXT    NOT NULL,
    max_downloads  INTEGER,
    download_count INTEGER NOT NULL DEFAULT 0,
    revoked        INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_shares_file ON shares(file_id);

CREATE TABLE IF NOT EXISTS audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    at         TEXT NOT NULL,
    actor      TEXT NOT NULL,
    action     TEXT NOT NULL,
    target     TEXT,
    ip         TEXT,
    detail     TEXT
);
CREATE INDEX IF NOT EXISTS idx_audit_at ON audit_log(at DESC);
"""


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        path: Path = current_app.config["DATABASE_PATH"]
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


def close_db(_exc=None) -> None:
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
