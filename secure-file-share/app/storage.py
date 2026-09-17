from __future__ import annotations

import hashlib
import os
import secrets
from pathlib import Path
from typing import BinaryIO, Iterator

from . import crypto


class _HashingReader:
    """Wraps a file object so the plaintext SHA-256 is computed during upload."""

    def __init__(self, stream: BinaryIO) -> None:
        self._stream = stream
        self._digest = hashlib.sha256()

    def read(self, size: int = -1) -> bytes:
        block = self._stream.read(size)
        self._digest.update(block)
        return block

    @property
    def hexdigest(self) -> str:
        return self._digest.hexdigest()


def blob_path(root: Path, blob_name: str) -> Path:
    return root / blob_name[:2] / blob_name


def store(stream: BinaryIO, root: Path, master_key: bytes) -> dict:
    """Encrypt ``stream`` to disk. Returns metadata for the database row."""
    dek = crypto.generate_key()
    blob_name = secrets.token_hex(16) + ".enc"
    path = blob_path(root, blob_name)
    path.parent.mkdir(parents=True, exist_ok=True)

    reader = _HashingReader(stream)
    tmp = path.with_suffix(".part")
    try:
        with open(tmp, "wb") as out:
            size = crypto.encrypt_stream(reader, out, dek)
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    finally:
        dek_wrapped = crypto.wrap_key(dek, master_key)
        dek = b"\x00" * len(dek)

    os.chmod(path, 0o600)
    return {
        "blob_name": blob_name,
        "size_bytes": size,
        "sha256": reader.hexdigest,
        "wrapped_key": dek_wrapped,
    }


def read(blob_name: str, wrapped_key: bytes, root: Path, master_key: bytes) -> Iterator[bytes]:
    dek = crypto.unwrap_key(wrapped_key, master_key)
    path = blob_path(root, blob_name)
    with open(path, "rb") as src:
        yield from crypto.decrypt_stream(src, dek)


def delete(blob_name: str, root: Path) -> None:
    blob_path(root, blob_name).unlink(missing_ok=True)
