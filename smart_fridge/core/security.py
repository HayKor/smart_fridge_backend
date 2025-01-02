from base64 import urlsafe_b64encode
from datetime import datetime, timedelta, timezone
from hashlib import blake2b
from typing import Any

from cryptography.fernet import Fernet
from jwt import decode as jwt_decode, encode as jwt_encode


class Encryptor:
    """Encryptor class for handling encryption, decryption, JWT encoding/decoding, and hashing."""

    def __init__(self, secret_key: str, jwt_algorithm: str, expire_minutes: int = 15, refresh_expire_days: int = 30):
        self.__secret_key = secret_key
        self.__jwt_algorithm = jwt_algorithm
        self.__expire_minutes = expire_minutes
        self.__refresh_expire_days = refresh_expire_days

    @property
    def jwt_expire_minutes(self) -> int:
        return self.__expire_minutes

    @property
    def jwt_refresh_expire_days(self) -> int:
        return self.__refresh_expire_days

    def encrypt_text(self, text: str, key: str = "") -> str:
        return Fernet(self.__get_encryption_key(key)).encrypt(text.encode()).decode()

    def decrypt_text(self, text: str, key: str = "") -> str:
        return Fernet(self.__get_encryption_key(key)).decrypt(text).decode()

    def encode_jwt(self, data: Any, expires_in: int | None = None) -> str:
        return jwt_encode(
            {
                "sub": str(data),
                "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_in or self.__expire_minutes),
            },
            self.__secret_key,
            algorithm=self.__jwt_algorithm,
        )

    def decode_jwt(self, token: str) -> dict[str, Any]:
        return jwt_decode(token, key=self.__secret_key, algorithms=[self.__jwt_algorithm])

    @staticmethod
    def hash_text(text: str | bytes, *, digest_size: int = 64, salt: str | bytes | None = None) -> str:
        return blake2b(
            (text if isinstance(text, bytes) else text.encode()),
            digest_size=digest_size,
            salt=((salt if isinstance(salt, bytes) else salt.encode()) if salt else b""),
        ).hexdigest()

    @staticmethod
    def hash_password(password: str, *, digest_size: int = 64) -> str:
        return Encryptor.hash_text(
            password,
            digest_size=digest_size,
            salt=Encryptor.hash_text(password[::2], digest_size=8),
        )

    def __get_encryption_key(self, key: str) -> bytes:
        return urlsafe_b64encode(Encryptor.hash_text(f"{key}{self.__secret_key}", digest_size=16).encode())
