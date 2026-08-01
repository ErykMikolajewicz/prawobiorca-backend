from typing import Protocol
from uuid import UUID

from app.application.dtos.regulations import RegulationRepresentation
from app.application.interfaces.relational import AsyncSession
from app.domain.value_objects.regulations import RegulationRegistrationData, RegulationType


class RegulationsStorage(Protocol):
    async def get_regulation(self, id_: UUID) -> bytes: ...

    async def upload_regulation(self, id_: UUID, file_data: bytes) -> None: ...

    async def delete_regulation(self, id_: UUID) -> None: ...


class RegulationsRepository(Protocol):
    def __init__(self): ...

    async def list_regulations(
        self, session: AsyncSession, user_id: UUID | None, regulation_type: RegulationType | None
    ) -> list[RegulationRepresentation]: ...

    async def register_regulation(
        self, session: AsyncSession, user_id: UUID | None, regulation_registration_data: RegulationRegistrationData
    ) -> UUID: ...

    async def unregister_regulation(self, session: AsyncSession, user_id: UUID | None, id_: UUID) -> None: ...

    async def mark_as_prepared(self, session: AsyncSession, user_id: UUID | None, id_: UUID) -> None: ...

    async def get_regulation_representation(
        self, session: AsyncSession, user_id: UUID | None, id_: UUID
    ) -> RegulationRepresentation | None: ...
