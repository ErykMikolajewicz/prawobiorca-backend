import secrets
from datetime import datetime, timedelta
from math import ceil

import bcrypt

from app.core.consts import BEARER_TOKEN_LENGTH


url_safe_bearer_token_length = ceil(BEARER_TOKEN_LENGTH * 4 / 3)


def hash_password(password: str) -> bytes:
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password


def generate_token() -> str:
    token = secrets.token_urlsafe(BEARER_TOKEN_LENGTH)
    return token


def get_expiration_date(expiration_in_seconds: int) -> datetime:
    return datetime.now() + timedelta(seconds=expiration_in_seconds)


def verify_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
