from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.core.logging_config import setup_logging
from app.api.router import include_all_routers
from app.relational_db.connection import engine, check_relational_db_connection
from app.vector_db.connection import qdrant_client, check_vector_db_connection


logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info('Connecting to external services.')
    await check_relational_db_connection()
    await check_vector_db_connection()
    app.state.ready = True
    logger.info('Application is ready to serve.')
    yield
    logger.info('Closing application.')
    await engine.dispose()
    await qdrant_client.close()

app = FastAPI(lifespan=lifespan, title='PRAWOBIORCA')

setup_logging()
include_all_routers(app)
