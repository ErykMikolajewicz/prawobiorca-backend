from fastapi import Request

from app.framework.web.templating import templates
from app.shared.consts import FLASH_KEY


def render_page_template(request: Request, page_name: str, **kwargs):
    flash_data = request.session.pop(FLASH_KEY, None)
    error_message = ""
    info_message = ""
    if flash_data:
        error_message = flash_data.get("error_message", "")
        info_message = flash_data.get("info_message", "")

    try:
        is_user_logged = request.state.user_id is not None
    except AttributeError:
        is_user_logged = False

    render_data = {
        "error_message": error_message,
        "info_message": info_message,
        "is_user_logged": is_user_logged,
    }

    render_data.update(**kwargs)
    return templates.TemplateResponse(request, page_name, render_data)
