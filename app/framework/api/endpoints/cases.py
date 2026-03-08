from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse

from app.application.use_cases.cases import AddCase, AddCaseArticle, DeleteCase, DeleteCaseArticle, ListCaseArticles
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.cases import (
    get_add_case_article,
    get_add_user_case,
    get_delete_case_article,
    get_delete_user_case,
    get_list_case_articles,
)
from app.framework.web.helpers import render_page_template

cases_router = APIRouter(tags=["cases"], dependencies=(Depends(set_user_by_session_id),))


@cases_router.get("/user/cases/{case_id}")
async def get_case_page(
    request: Request, case_id: str, list_case_articles: Annotated[ListCaseArticles, Depends(get_list_case_articles)]
):
    articles = await list_case_articles.execute()
    return render_page_template(request, "case_page.html", case_id=case_id, articles=articles)


@cases_router.post("/user/cases")
async def add_user_case(add_user_case_: Annotated[AddCase, Depends(get_add_user_case)]):
    await add_user_case_.execute()

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@cases_router.post("/user/cases/delete")
async def delete_user_case(delete_user_case_: Annotated[DeleteCase, Depends(get_delete_user_case)]):
    await delete_user_case_.execute()

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@cases_router.post("/user/cases/articles")
async def add_case_article(add_case_article_: Annotated[AddCaseArticle, Depends(get_add_case_article)]):
    await add_case_article_.execute()

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@cases_router.delete("/user/cases/articles/{articleId}")
async def delete_case_article(delete_case_article_: Annotated[DeleteCaseArticle, Depends(get_delete_case_article)]):
    await delete_case_article_.execute()

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
