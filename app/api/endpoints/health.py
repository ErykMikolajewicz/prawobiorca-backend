import logging
from typing import Literal

from fastapi import APIRouter, HTTPException, Request, status
from grpc import RpcError
from sqlalchemy.exc import InterfaceError

from app.relational_db.connection import check_relational_db_connection
from app.vector_db.connection import check_vector_db_connection

logger = logging.getLogger(__name__)

health_router = APIRouter(
    prefix="/health",
    tags=["health check"],
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Service unavailable."}},
)


@health_router.get("/liveness")
async def get_health_status() -> Literal["OK"]:
    logger.info("Checking liveness.")

    unavailable_services = []

    try:
        await check_relational_db_connection()
    except InterfaceError:
        logger.error("Can not connect to relational database!", exc_info=True)
        unavailable_services.append("relational database")

    try:
        await check_vector_db_connection()
    except RpcError:
        logger.error("Can not connect to vector database!", exc_info=True)
        unavailable_services.append("vector database")

    if unavailable_services:
        unavailable_services = ", ".join(unavailable_services)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Could not connect to: {unavailable_services}"
        )

    return "OK"


@health_router.get("/ready", summary="Check is application ready to response for requests.")
async def check_readiness(request: Request) -> Literal[True]:
    try:
        is_ready = request.app.state.ready
    except AttributeError:
        logger.warning("Application is not ready to serve yet.", exc_info=True)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Application not ready yet")
    if is_ready:
        return is_ready
    else:
        logger.critical("Application is in invalid readiness state!.", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid application state!")
