from fastapi import APIRouter, Request, status
from app.framework.web.templating import templates

login_router = APIRouter(tags=["login_html"])


@login_router.get("/login", status_code=status.HTTP_200_OK)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})