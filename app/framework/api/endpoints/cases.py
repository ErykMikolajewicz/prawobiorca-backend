from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse

from app.application.use_cases.cases import AddCase
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.cases import get_add_user_case

cases_router = APIRouter(tags=["cases"], dependencies=(Depends(set_user_by_session_id),))


@cases_router.post("/user/cases")
async def add_user_case(add_user_case_: Annotated[AddCase, Depends(get_add_user_case)]):
    await add_user_case_.execute()

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
