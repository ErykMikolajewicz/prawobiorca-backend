from fastapi import status

from app.framework.dependencies.authentication import refresh_tokens_provider


def test_refresh_missing_header(client, assure_use_case_not_executed):
    assure_use_case_not_executed(refresh_tokens_provider)

    response = client.post("/auth/refresh")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_refresh_empty_token(client, assure_use_case_not_executed):
    assure_use_case_not_executed(refresh_tokens_provider)

    headers = {"X-Refresh-Token": ""}
    response = client.post("/auth/refresh", headers=headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
