from fastapi import FastAPI

from app.framework.api.endpoints.auth import auth_router
from app.framework.api.endpoints.files import files_router
from app.framework.api.endpoints.health import health_router
from app.framework.api.endpoints_html.accounts import account_router
from app.framework.api.endpoints_html.auth import auth_router as html_auth_router
from app.framework.api.endpoints_html.files import html_files_router
from app.framework.api.endpoints_html.main_page import main_page_router
from app.framework.api.endpoints_html.search import search_router


def include_all_routers(app: FastAPI):
    app.include_router(account_router)
    app.include_router(auth_router)
    app.include_router(files_router)
    app.include_router(health_router)
    app.include_router(main_page_router)
    app.include_router(html_files_router)
    app.include_router(search_router)
    app.include_router(html_auth_router)
