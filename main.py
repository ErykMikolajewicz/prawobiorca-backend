import logging
import tomllib
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI

from app.framework.api.router import include_all_routers
from app.infrastructure.file_storage.connection import check_file_storage_connection
from app.infrastructure.key_value_db.connection import check_key_value_db_connection
from app.infrastructure.relational_db.connection import check_relational_db_connection
from app.infrastructure.vector_db.connection import check_vector_db_connection
from app.shared.logging_config import setup_logging

logger = logging.getLogger("app")
with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

version = data["project"]["version"]


@asynccontextmanager
async def lifespan(_: FastAPI):
    closing_callbacks = []

    logger.info("Connecting to external services.")
    try:
        relational_closing_callback = await check_relational_db_connection()
        closing_callbacks.insert(0, relational_closing_callback)

        key_value_closing_callback = await check_key_value_db_connection()
        closing_callbacks.insert(0, key_value_closing_callback)

        vector_db_closing_callback = await check_vector_db_connection()
        closing_callbacks.insert(0, vector_db_closing_callback)

        file_storage_closing_callback = await check_file_storage_connection()
        closing_callbacks.insert(0, file_storage_closing_callback)
    except Exception as e:
        logger.critical(f'Can not connect to external service: {e}')
        raise
    else:
        app.state.ready = True
        logger.info("Application is ready to serve.")
        yield
    finally:
        logger.info("Closing application.")
        app.state.ready = False

        for callback in closing_callbacks:
            try:
                async with asyncio.timeout(30):
                    await callback()
            except Exception as e:
                logger.error(f'Error during clean up: {e}')


app = FastAPI(lifespan=lifespan, title="PRAWOBIORCA", version=version)

setup_logging()
include_all_routers(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
