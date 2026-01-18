"""
Pytest configuration file for the FastAPI project.

Contains common fixtures used in tests, such as the FastAPI test client
and generators for tokens and UUIDs.
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.domain.services.security import url_safe_bearer_token_length, url_safe_email_verification_token_length
from app.main import app


@pytest.fixture
def bearer_token_generator() -> Generator[str, None]:
    """
    Pytest fixture that generates a sequence of url-safe bearer tokens.

    The tokens are pre-defined and asserted to match the
    `url_safe_bearer_token_length`.

    Can be used max 3 times, currently sufficient for all tests scenarios.

    Yields:
        str: The next bearer token from the predefined list.
    """

    def get_token() -> Generator[str, None]:
        tokens = (
            "O8KwTwMvXTSn3VdWl6iZlNqmw39UvFRvIbeHfo-mykY",
            "XzkNQQKM3CYn3ncRcs-c2txIxihTk_Mi126sebi06VA",
            "CKIr3mwWTEXoMNaHl7Q4-jjz8oowSPBIayMSTe2UXxg",
        )
        for token in tokens:
            assert len(token) == url_safe_bearer_token_length
            yield token

    return get_token()


@pytest.fixture
def uuid_generator() -> Generator[str, None]:
    """
    Pytest fixture that generates a sequence of predefined UUIDs.

    Used to provide consistent UUID values in tests.

    Can be used max 3 times, currently sufficient for all tests scenarios.

    Yields:
        str: The next UUID from the predefined list.
    """

    def get_uuid() -> Generator[str, None]:
        uuids = (
            "1b4a1b7a-dbd6-4be4-a52e-80fdd9ddbfb0",
            "ad987bb3-cf5b-4d07-a23c-2e5f1221171a",
            "4596f6de-d067-4e36-ad9f-a3b3959eee6b",
        )
        for uuid_ in uuids:
            yield uuid_

    return get_uuid()


@pytest.fixture
def email_token_generator() -> Generator[str, None]:
    """
    Pytest fixture that generates a sequence of URL-safe email verification tokens.

    The tokens are pre-defined and asserted to match the
    `url_safe_email_verification_token_length`.

    Can be used max 1 times, currently sufficient for all tests scenarios.

    Yields:
        str: The next email verification token from the predefined list.
    """

    def get_token() -> Generator[str, None]:
        tokens = ("csca-AVXPdclA0dJlSLhgGc1sWpaPOxVTiHjVfTLyog",)
        for token in tokens:
            assert len(token) == url_safe_email_verification_token_length
            yield token

    return get_token()


@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    Pytest fixture that provides a FastAPI test client.

    The test client is initialized once per test session (`scope="session"`)
    and allows making HTTP requests to the FastAPI application instance
    without running a server.

    Returns:
        fastapi.testclient.TestClient: The FastAPI test client.
    """
    return TestClient(app)
