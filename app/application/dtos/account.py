from dataclasses import dataclass
from app.domain.services.security import Secret


@dataclass
class AccountData:
    email: str
    password: Secret
