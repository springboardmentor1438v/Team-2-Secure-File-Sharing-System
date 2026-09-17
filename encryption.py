from cryptography.fernet import Fernet


def generate_file_key() -> str:
    """
    Generate a unique symmetric encryption key (URL-safe base64-encoded).
    Uses 128-bit AES in CBC mode with 128-bit HMAC authentication (Fernet).
    """
    return Fernet.generate_key().decode()


def encrypt_file(data: bytes, key: str | bytes) -> bytes:
    """
    Encrypt file content using the provided key.
    """
    if isinstance(key, str):
        key = key.encode()
    fernet = Fernet(key)
    return fernet.encrypt(data)


def decrypt_file(data: bytes, key: str | bytes) -> bytes:
    """
    Decrypt encrypted file content using the provided key.
    """
    if isinstance(key, str):
        key = key.encode()
    fernet = Fernet(key)
    return fernet.decrypt(data)
