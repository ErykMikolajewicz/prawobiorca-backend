from uuid import uuid4

from app.config import settings
from app.core.security import generate_token, url_safe_bearer_token_length

invalid_bearer_token = "a" * url_safe_bearer_token_length
valid_bearer_token = generate_token()  # It is random, not valid in sense exist in database
user_id = str(uuid4())
access_token_expiration_seconds = settings.app.ACCESS_TOKEN_EXPIRATION_SECONDS
refresh_token_expiration_seconds = settings.app.REFRESH_TOKEN_EXPIRATION_SECONDS
