from cryptography.fernet import Fernet

KEY_PATH = "security/key.key"


def load_key():
    with open(KEY_PATH, "rb") as key_file:
        return key_file.read()


key = load_key()
fernet = Fernet(key)


def encrypt_file(file_data: bytes):
    return fernet.encrypt(file_data)




from cryptography.fernet import Fernet, InvalidToken

def decrypt_file(file_data: bytes):
    try:
        return fernet.decrypt(file_data)
    except InvalidToken:
        raise Exception("Encrypted file is corrupted")