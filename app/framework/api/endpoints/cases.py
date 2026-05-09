from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.cases import CaseData
from app.application.use_cases.cases import (
    AddCase,
    AddCaseArticle,
    DeleteCase,
    DeleteCaseArticle,
    ListCaseArticles,
    ListCases,
)
from app.domain.exceptions import CaseNotFound
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.cases import (
    get_add_case_article,
    get_add_user_case,
    get_delete_case_article,
    get_delete_user_case,
    get_list_case_articles,
    get_list_user_cases,
)

cases_router = APIRouter(tags=["cases"], dependencies=(Depends(set_user_by_session_id),), prefix="/api")


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
async def delete_user_case(delete_user_case_: Annotated[DeleteCase, Depends(get_delete_user_case)]):
    try:
        await delete_user_case_.execute()
    except CaseNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No case with that id!")


@cases_router.post(
    "/user/cases/{caseId}/articles",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "No case with that id!"},
    },
)
async def add_case_article(add_case_article_: Annotated[AddCaseArticle, Depends(get_add_case_article)]):
    try:
        await add_case_article_.execute()
    except CaseNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No case with that id!")


@cases_router.get("/user/cases/{caseId}/articles")
async def get_case_articles(list_case_articles: Annotated[ListCaseArticles, Depends(get_list_case_articles)]):
    articles = await list_case_articles.execute()
    return articles


@cases_router.delete("/user/cases/articles/{articleId}")
async def delete_case_article(delete_case_article_: Annotated[DeleteCaseArticle, Depends(get_delete_case_article)]):
    await delete_case_article_.execute()
