from fastapi import FastAPI

from app.framework.api.endpoints.accounts import account_router
from app.framework.api.endpoints.auth import auth_router
from app.framework.api.endpoints.health import health_router
from app.framework.api.endpoints.user_files import user_files_router
from prawobiorca.app.framework.api.endpoints.extract_document import extract_document_router


def include_all_routers(app: FastAPI):
    app.include_router(account_router)
    app.include_router(auth_router)
    app.include_router(user_files_router)
    app.include_router(health_router)
    app.include_router(extract_document_router)
