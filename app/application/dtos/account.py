from dataclasses import dataclass

from app.domain.services.security import Secret


@dataclass
class LoginData:
    email: str
    password: Secret
