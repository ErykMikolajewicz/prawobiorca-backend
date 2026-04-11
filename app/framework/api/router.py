from fastapi import FastAPI

import app.framework.api.endpoints.v2.accounts as v2_accounts
import app.framework.api.endpoints.v2.auth as v2_auth
import app.framework.api.endpoints.v2.cases as v2_cases
import app.framework.api.endpoints.v2.public_files as v2_files
import app.framework.api.endpoints.v2.user_files as v2_user_files
from app.framework.api.endpoints.accounts import account_router
from app.framework.api.endpoints.auth import auth_router
from app.framework.api.endpoints.cases import cases_router
from app.framework.api.endpoints.health import health_router
from app.framework.api.endpoints.main_page import main_page_router
from app.framework.api.endpoints.search_public import public_search_router
from app.framework.api.endpoints.search_user_file import user_file_search_router
from app.framework.api.endpoints.user_files import user_files_router


def include_all_routers(app: FastAPI):
    app.include_router(account_router)
    app.include_router(auth_router)
    app.include_router(health_router)
    app.include_router(main_page_router)
    app.include_router(public_search_router)
    app.include_router(cases_router)
    app.include_router(user_files_router)
    app.include_router(user_file_search_router)

    app.include_router(v2_auth.auth_router)
    app.include_router(v2_files.public_files_router)
    app.include_router(v2_accounts.account_router)
    app.include_router(v2_cases.cases_router)
    app.include_router(v2_user_files.user_files_router)
