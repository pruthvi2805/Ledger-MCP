import os
import hashlib
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from typing import Tuple

class Security:
    @staticmethod
    def generate_salt() -> bytes:
        return os.urandom(16)

    @staticmethod
    def derive_key(password: str, salt: bytes, iterations: int = 480000) -> bytes:
        """Derives a session key from the master password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    @staticmethod
    def encrypt_secret(key: bytes, plaintext: str) -> bytes:
        """Encrypts sensitive config data (e.g. bank passwords)."""
        f = Fernet(key)
        return f.encrypt(plaintext.encode())

    @staticmethod
    def decrypt_secret(key: bytes, ciphertext: bytes) -> str:
        """Decrypts sensitive config data."""
        f = Fernet(key)
        return f.decrypt(ciphertext).decode()

    @staticmethod
    def generate_transaction_id(date: str, amount_int: int, description: str, source_file: str) -> str:
        """
        Collision-proof ID generation.
        Format: sha256("date|amount|description|source_file")
        """
        raw_string = f"{date}|{amount_int}|{description}|{source_file}"
        return hashlib.sha256(raw_string.encode()).hexdigest()

