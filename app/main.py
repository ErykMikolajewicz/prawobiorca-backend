import logging
import tomllib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool

from app.api.router import include_all_routers
from app.infrastructure.cloud_storage.connection import check_cloud_storage_connection, storage_client
from app.shared.logging_config import setup_logging
from app.infrastructure.key_value_db.connection import check_redis_connection, redis_pool
from app.infrastructure.relational_db.connection import check_relational_db_connection, engine
from app.infrastructure.vector_db import check_vector_db_connection, qdrant_client

logger = logging.getLogger("app")
with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

version = data["project"]["version"]


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Connecting to external services.")
    await check_relational_db_connection()
    await check_redis_connection()
    await check_vector_db_connection()
    await run_in_threadpool(check_cloud_storage_connection)
    app.state.ready = True
    logger.info("Application is ready to serve.")
    yield
    logger.info("Closing application.")
    await qdrant_client.close()
    await redis_pool.disconnect()
    await engine.dispose()
    storage_client.close()


app = FastAPI(lifespan=lifespan, title="PRAWOBIORCA", version=version)

setup_logging()
include_all_routers(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
