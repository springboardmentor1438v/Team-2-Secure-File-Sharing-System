from __future__ import annotations

import base64
import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    """Minimal .env reader so the project has no extra dependency."""
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


_load_dotenv(BASE_DIR / ".env")


class Config:
    # --- secrets -------------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

    #: 32-byte AES master key, base64url encoded. Generate with:
    #:   python -c "import os,base64;print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
    MASTER_KEY_B64 = os.environ.get("MASTER_KEY")

    # --- storage -------------------------------------------------------
    STORAGE_DIR = Path(os.environ.get("STORAGE_DIR", BASE_DIR / "storage"))
    DATABASE_PATH = Path(os.environ.get("DATABASE_PATH", BASE_DIR / "storage" / "vault.db"))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_MB", "200")) * 1024 * 1024

    # --- policy --------------------------------------------------------
    DEFAULT_LINK_TTL_HOURS = int(os.environ.get("DEFAULT_LINK_TTL_HOURS", "24"))
    MAX_LINK_TTL_HOURS = int(os.environ.get("MAX_LINK_TTL_HOURS", str(24 * 30)))
    MIN_PASSWORD_LENGTH = 12
    LOGIN_RATE_LIMIT = (8, 300)      # 8 attempts per 5 minutes per IP
    UNLOCK_RATE_LIMIT = (10, 600)    # 10 share-password attempts per 10 minutes

    # --- cookies / transport -------------------------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_NAME = "sfs_session"
    #: keep False for local http development, True behind TLS in production
    SESSION_COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "0") == "1"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8

    @classmethod
    def master_key(cls) -> bytes:
        if not cls.MASTER_KEY_B64:
            raise RuntimeError(
                "MASTER_KEY is not set. Create a .env file (see .env.example) "
                "or run: python run.py --init"
            )
        key = base64.urlsafe_b64decode(cls.MASTER_KEY_B64)
        if len(key) != 32:
            raise RuntimeError("MASTER_KEY must decode to exactly 32 bytes")
        return key
