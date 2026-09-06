from uuid import UUID

from src.domain.services.security import create_access_token
from src.domain.value_objects.auth import AccessTokenClaims
from src.shared.settings.application import app_settings

STRONG_PASSWORD = "StrongPassword12;"

VALID_USERNAME = "username123"
ADMIN_USERNAME = "admin123"

USER_ID = UUID("edcd61d8-5026-4f71-850d-b5e072601fb3")
ADMIN_ID = UUID("1a12354a-0f96-4dad-aaf1-b777a5596381")
UNKNOWN_USER_ID = UUID("3f0c1d2e-8a4b-4c6d-9e1f-7b2a5c8d3e40")

SESSION_ID = UUID("6e5a5b3c-1f1b-4f6a-9a4e-2c9c6f0d9b21")

REFRESH_TOKEN = "O8KwTwMvXTSn3VdWl6iZlNqmw39UvFRvIbeHfo-mykY"

UNKNOWN_REFRESH_TOKEN = "kGG09w8Igs09xBw7ki-oZ-F_kPQC0Hs9tbCyWaKm8fs"

EMBEDDING_SERVICE_PORT = 8080
EXTRACTION_SERVICE_PORT = 8080


def build_access_token(user_id: UUID = USER_ID, session_id: UUID = SESSION_ID, is_admin: bool = False) -> str:
    claims = AccessTokenClaims(user_id=user_id, session_id=session_id, is_admin=is_admin)

    return create_access_token(
        claims, app_settings.JWT_SECRET_KEY, app_settings.JWT_ALGORITHM, app_settings.ACCESS_TOKEN_EXPIRATION_SECONDS
    )


ACCESS_TOKEN = build_access_token()

UNKNOWN_ACCESS_TOKEN = build_access_token(user_id=UNKNOWN_USER_ID)
