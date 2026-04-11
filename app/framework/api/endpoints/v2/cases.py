from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.cases import CaseData
from app.application.use_cases.cases import ListCases
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.cases import get_list_user_cases

cases_router = APIRouter(tags=["cases"], dependencies=(Depends(set_user_by_session_id),), prefix="/v2")


@cases_router.get("/user/cases", responses={status.HTTP_204_NO_CONTENT: {"description": "No user cases."}})
async def get_cases_list(
    list_cases: Annotated[ListCases, Depends(get_list_user_cases)],
) -> list[CaseData]:
    cases = await list_cases.execute()
    if cases:
        return cases
    else:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No cases for that user.")
