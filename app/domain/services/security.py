import asyncio
import secrets
from math import ceil

import bcrypt
from pydantic import SecretStr

from app.shared.consts import SECURITY_MIN_RESPONSE_TIME, SESSION_ID_LENGTH

url_safe_session_id_length = ceil(SESSION_ID_LENGTH * 4 / 3)


def hash_password(password: SecretStr) -> bytes:
    password = password.get_secret_value()
    password = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    return hashed_password


def generate_session_id(session_id_length: int = SESSION_ID_LENGTH) -> str:
    session_id = secrets.token_urlsafe(session_id_length)
    return session_id


def verify_password(password: SecretStr, hashed_password: bytes) -> bool:
    password = password.get_secret_value()
    password = password.encode("utf-8")
    return bcrypt.checkpw(password, hashed_password)


async def prevent_timing_attack(execution_start_time: float):
    elapsed_execution_time = asyncio.get_event_loop().time() - execution_start_time
    delay = max(0.0, SECURITY_MIN_RESPONSE_TIME - elapsed_execution_time)
    await asyncio.sleep(delay)
