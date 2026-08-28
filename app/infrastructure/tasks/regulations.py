from dataclasses import dataclass
from typing import Any
from uuid import UUID

from taskiq.kicker import AsyncKicker

from app.shared.consts import REGULATION_PREPARATION_TASK_NAME


@dataclass
class TaskiqRegulationPreparationScheduler:
    broker: Any

    async def schedule_regulation_preparation(self, user_id: UUID | None, regulation_id: UUID) -> None:
        await AsyncKicker(REGULATION_PREPARATION_TASK_NAME, self.broker, labels={}).kiq(
            str(user_id) if user_id is not None else None, str(regulation_id)
        )
