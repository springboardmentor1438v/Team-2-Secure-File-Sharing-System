"""Envelope encryption for file contents.

Design
------
* Every uploaded file gets its own random 256-bit data key (DEK).
* The DEK never touches the disk in plaintext: it is wrapped with the
  master key (KEK) from the environment using AES-256-GCM and stored in
  the database alongside the file record.
* File bytes are encrypted in fixed-size chunks so that arbitrarily large
  uploads can be streamed without loading them into memory. Each chunk is
  sealed with AES-256-GCM under a nonce of base_nonce || chunk_counter,
  which guarantees nonce uniqueness for a given DEK.
* The final chunk is flagged inside its associated data, so truncating the
  ciphertext is detected at decryption time instead of silently returning a
  shorter file.

On-disk layout of an encrypted blob:

    magic "SFSv1"        5 bytes
    base_nonce           8 bytes
    repeated chunks:
        length           4 bytes, big endian, length of sealed chunk
        sealed chunk     ciphertext + 16 byte GCM tag
"""

from __future__ import annotations

import os
import struct
from typing import BinaryIO, Iterator

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"SFSv1"
CHUNK_SIZE = 64 * 1024
NONCE_PREFIX_LEN = 8
KEY_LEN = 32


class DecryptionError(Exception):
    """Raised when a blob fails authentication or is malformed."""


def generate_key() -> bytes:
    return os.urandom(KEY_LEN)


def wrap_key(dek: bytes, kek: bytes) -> bytes:
    """Encrypt a data key with the master key. Returns nonce || ciphertext."""
    nonce = os.urandom(12)
    return nonce + AESGCM(kek).encrypt(nonce, dek, b"sfs-dek")


def unwrap_key(wrapped: bytes, kek: bytes) -> bytes:
    nonce, blob = wrapped[:12], wrapped[12:]
    try:
        return AESGCM(kek).decrypt(nonce, blob, b"sfs-dek")
    except InvalidTag as exc:  # wrong master key, or tampered row
        raise DecryptionError("data key could not be unwrapped") from exc


def _chunk_nonce(prefix: bytes, counter: int) -> bytes:
    return prefix + struct.pack(">I", counter)


def encrypt_stream(src: BinaryIO, dst: BinaryIO, dek: bytes) -> int:
    """Encrypt ``src`` into ``dst``. Returns the plaintext byte count."""
    aead = AESGCM(dek)
    prefix = os.urandom(NONCE_PREFIX_LEN)
    dst.write(MAGIC)
    dst.write(prefix)

    counter = 0
    plaintext_size = 0
    pending = src.read(CHUNK_SIZE)
    while True:
        block = src.read(CHUNK_SIZE)
        is_final = not block
        aad = b"final" if is_final else b"chunk"
        sealed = aead.encrypt(_chunk_nonce(prefix, counter), pending, aad)
        dst.write(struct.pack(">I", len(sealed)))
        dst.write(sealed)
        plaintext_size += len(pending)
        counter += 1
        if is_final:
            break
        pending = block
    return plaintext_size


def decrypt_stream(src: BinaryIO, dek: bytes) -> Iterator[bytes]:
    """Yield decrypted plaintext chunks from an encrypted blob."""
    if src.read(len(MAGIC)) != MAGIC:
        raise DecryptionError("not a valid encrypted blob")
    prefix = src.read(NONCE_PREFIX_LEN)
    if len(prefix) != NONCE_PREFIX_LEN:
        raise DecryptionError("truncated header")

    aead = AESGCM(dek)
    counter = 0
    saw_final = False
    while True:
        header = src.read(4)
        if not header:
            break
        if len(header) != 4:
            raise DecryptionError("truncated chunk header")
        (size,) = struct.unpack(">I", header)
        sealed = src.read(size)
        if len(sealed) != size:
            raise DecryptionError("truncated chunk body")
        nonce = _chunk_nonce(prefix, counter)
        try:
            yield aead.decrypt(nonce, sealed, b"chunk")
        except InvalidTag:
            try:
                yield aead.decrypt(nonce, sealed, b"final")
                saw_final = True
            except InvalidTag as exc:
                raise DecryptionError("chunk failed authentication") from exc
        counter += 1
        if saw_final:
            break
    if not saw_final:
        raise DecryptionError("blob ended without a final chunk")
