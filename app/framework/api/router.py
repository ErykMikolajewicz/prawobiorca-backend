from fastapi import FastAPI

from app.framework.api.endpoints.accounts import account_router
from app.framework.api.endpoints.auth import auth_router
from app.framework.api.endpoints.health import health_router
from app.framework.api.endpoints.user_files import user_files_router
from app.framework.api.endpoints_html.main_page import main_page_router
from app.framework.api.endpoints_html.files import files_router
from app.framework.api.endpoints_html.search import search_router
from app.framework.api.endpoints.divide_document import divide_document_router


def include_all_routers(app: FastAPI):
    app.include_router(account_router)
    app.include_router(auth_router)
    app.include_router(user_files_router)
    app.include_router(health_router)
    app.include_router(divide_document_router)
    app.include_router(main_page_router)
    app.include_router(files_router)
    app.include_router(search_router)
