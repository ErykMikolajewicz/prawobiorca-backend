import json

import pytest
from fastapi import status

from app.domain.value_objects.regulations import RegulationType
from app.shared.consts import AUTHORIZATION_COOKIE_NAME
from tests.consts import AUTHORIZATION_TOKEN, UNKNOWN_AUTHORIZATION_TOKEN


@pytest.mark.parametrize(
    "file_name, file_type, error_status",
    [
        ("", RegulationType.STATUTE, status.HTTP_422_UNPROCESSABLE_CONTENT),
        ("a" * 300, RegulationType.ACT, status.HTTP_422_UNPROCESSABLE_CONTENT),
        ("file.txt", "invalid_regulation_type", status.HTTP_422_UNPROCESSABLE_CONTENT),
    ],
    ids=("empty file name", "file name too long", "invalid regulation type"),
)
def test_logged_used_add_public_regulation_validation(
    client,
    override_get_regulations_storage,
    override_authorize_admin_user,
    file_name,
    file_type,
    error_status,
):
    regulation_data = {"name": file_name, "regulation_type": file_type}

    cookies = {AUTHORIZATION_COOKIE_NAME: AUTHORIZATION_TOKEN}
    client.cookies = cookies

    response = client.post("api/user/regulations", json=regulation_data)

    assert response.status_code == error_status


def test_unauthorized_user_add_public_regulation(client, override_authorize_admin_user):
    regulation_data = {"name": "test.txt", "regulation_type": RegulationType.DECREE}

    session_data = {"session_id": UNKNOWN_AUTHORIZATION_TOKEN}
    cookie_value = json.dumps(session_data)

    cookies = {AUTHORIZATION_COOKIE_NAME: cookie_value}
    client.cookies = cookies

    response = client.post("api/user/regulations", json=regulation_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_non_admin_user_add_public_regulation(client, override_authorize_normal_user):
    regulation_data = {"name": "test.txt", "regulation_type": RegulationType.DECREE}

    cookies = {AUTHORIZATION_COOKIE_NAME: AUTHORIZATION_TOKEN}
    client.cookies = cookies

    response = client.post("api/regulations", json=regulation_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
