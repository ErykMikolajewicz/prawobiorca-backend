import secrets
from datetime import datetime, timedelta

import bcrypt


def hash_password(password: str) -> bytes:
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password


def generate_token() -> str:
    token = secrets.token_urlsafe(32)
    return token


def get_expiration_date(expiration_in_minutes) -> datetime:
    return datetime.now() + timedelta(minutes=expiration_in_minutes)


def verify_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
