from typing import Any, Awaitable, Callable

from taskiq import SimpleRetryMiddleware
from taskiq_redis import ListQueueBroker

from app.domain.exceptions.regulations import RegulationServiceUnavailable
from app.shared.consts import MAX_REGULATION_PREPARATION_ATTEMPTS
from app.shared.settings.broker import broker_settings

broker = ListQueueBroker(url=broker_settings.URL).with_middlewares(
    SimpleRetryMiddleware(
        default_retry_count=MAX_REGULATION_PREPARATION_ATTEMPTS,
        default_retry_label=True,
        types_of_exceptions=[RegulationServiceUnavailable],
    )
)


async def init_broker() -> tuple[Any, Callable[..., Awaitable[None]]]:
    await broker.startup()
    return broker, broker.shutdown
