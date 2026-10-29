import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import settings


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fernet() -> Fernet:
    if settings.FERNET_KEY:
        key = settings.FERNET_KEY.encode()
    else:
        # Deterministic local-development fallback. Set FERNET_KEY in production.
        key = base64.urlsafe_b64encode(hashlib.sha256(settings.JWT_SECRET_KEY.encode()).digest())
    return Fernet(key)


def encrypt(data: bytes) -> bytes:
    return _fernet().encrypt(data)


def decrypt(data: bytes) -> bytes:
    return _fernet().decrypt(data)
