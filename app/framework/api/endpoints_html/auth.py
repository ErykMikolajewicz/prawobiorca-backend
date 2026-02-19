from fastapi import APIRouter, Request, status

from app.framework.web.templating import templates

auth_router = APIRouter(tags=["auth"])


@auth_router.get("/login", status_code=status.HTTP_200_OK)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
