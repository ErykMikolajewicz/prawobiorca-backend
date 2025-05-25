from fastapi import FastAPI

from app.api.endpoints.health import health_router
from app.api.endpoints.account import account_router
from app.api.endpoints.files import files_router


def include_all_routers(app: FastAPI):
    app.include_router(account_router)
    app.include_router(files_router)
    app.include_router(health_router)
