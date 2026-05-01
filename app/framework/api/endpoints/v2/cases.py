from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.cases import CaseData
from app.application.use_cases.cases import AddCase, DeleteCase, ListCases
from app.domain.exceptions import CaseNotFound
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.cases import get_add_user_case, get_delete_user_case_v2, get_list_user_cases

cases_router = APIRouter(tags=["cases"], dependencies=(Depends(set_user_by_session_id),), prefix="/api/v2")


@cases_router.get("/user/cases", responses={status.HTTP_204_NO_CONTENT: {"description": "No user cases."}})
async def get_cases_list(
    list_cases: Annotated[ListCases, Depends(get_list_user_cases)],
) -> list[CaseData]:
    cases = await list_cases.execute()
    if cases:
        return cases
    else:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No cases for that user.")


@cases_router.post("/user/cases")
async def add_user_case(add_user_case_: Annotated[AddCase, Depends(get_add_user_case)]) -> UUID:
    case_id = await add_user_case_.execute()
    return case_id


@cases_router.delete(
    "/user/cases/{caseId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Case deleted."},
        status.HTTP_404_NOT_FOUND: {"description": "No case with that id!"},
    },
)
async def delete_user_case(delete_user_case_: Annotated[DeleteCase, Depends(get_delete_user_case_v2)]):
    try:
        await delete_user_case_.execute()
    except CaseNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No case with that id!")
