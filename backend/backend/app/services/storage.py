from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.services.crypto import decrypt, encrypt


def store_encrypted(data: bytes, category: str) -> str:
    root = settings.STORAGE_ROOT.resolve()
    directory = root / category
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{uuid4().hex}.enc"
    path.write_bytes(encrypt(data))
    return str(path)


def read_decrypted(storage_path: str) -> bytes:
    path = Path(storage_path).resolve()
    root = settings.STORAGE_ROOT.resolve()
    if root not in path.parents or not path.is_file():
        raise FileNotFoundError("Stored file is unavailable")
    return decrypt(path.read_bytes())
