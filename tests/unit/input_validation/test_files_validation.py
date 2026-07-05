import json

import pytest
from fastapi import status

from app.domain.value_objects.regulations import RegulationType
from app.shared.consts import AUTHORIZATION_COOKIE_NAME
from tests.consts import AUTHORIZATION_TOKEN, UNKNOWN_AUTHORIZATION_TOKEN


@pytest.mark.parametrize(
    "file_name, file_content, file_type, error_status",
    [
        ("file.txt", b"", RegulationType.DECREE, status.HTTP_400_BAD_REQUEST),
        ("", b"valid_content", RegulationType.STATUTE, status.HTTP_422_UNPROCESSABLE_CONTENT),
        ("a" * 300, b"valid_content", RegulationType.ACT, status.HTTP_400_BAD_REQUEST),
        ("file.txt", b"valid_content", "invalid_regulation_type", status.HTTP_422_UNPROCESSABLE_CONTENT),
    ],
    ids=("empty file", "empty file name", "file name too long", "invalid regulation type"),
)
def test_logged_used_add_public_regulation_validation(
    client,
    override_get_regulations_repository,
    override_authorize_admin_user,
    file_name,
    file_content,
    file_type,
    error_status,
):
    files = {"regulation": (file_name, file_content, "plain/text")}
    params = {"regulation_type": file_type}

    session_data = {"session_id": AUTHORIZATION_TOKEN}
    cookie_value = json.dumps(session_data)

    cookies = {AUTHORIZATION_COOKIE_NAME: cookie_value}
    client.cookies = cookies

    response = client.post("api/user/regulations", files=files, params=params)

    assert response.status_code == error_status


def test_unauthorized_user_add_public_regulation(client, override_authorize_admin_user):
    files = {"regulation": ("test.txt", b"valid_content", "plain/text")}
    params = {"regulation_type": RegulationType.DECREE}

    session_data = {"session_id": UNKNOWN_AUTHORIZATION_TOKEN}
    cookie_value = json.dumps(session_data)

    cookies = {AUTHORIZATION_COOKIE_NAME: cookie_value}
    client.cookies = cookies

    response = client.post("api/user/regulations", files=files, params=params)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_non_admin_user_add_public_regulation(client, override_authorize_normal_user):
    files = {"regulation": ("test.txt", b"valid_content", "plain/text")}
    params = {"regulation_type": RegulationType.DECREE}

    session_data = {"session_id": AUTHORIZATION_TOKEN}
    cookie_value = json.dumps(session_data)

    cookies = {AUTHORIZATION_COOKIE_NAME: cookie_value}
    client.cookies = cookies

    response = client.post("api/regulations", files=files, params=params)

    assert response.status_code == status.HTTP_403_FORBIDDEN
