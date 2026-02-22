"""
Pytest configuration file for the FastAPI project.

Contains common fixtures used in tests, such as the FastAPI test client
and generators for tokens and UUIDs.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.domain.services.security import url_safe_session_id_length
from main import app


@pytest.fixture(scope="function")
def session_id_generator() -> Iterator[str]:
    """
    Generates a sequence of url-safe session id.

    The session id is pre-defined and asserted to match the
    `url_safe_session_id_length`.

    Can be used max 1 time p test, currently sufficient for all test scenarios.

    Yields:
        str: The next session id from the predefined sequence.
    """

    session_ids = ("O8KwTwMvXTSn3VdWl6iZlNqmw39UvFRvIbeHfo-mykY",)
    for session_id in session_ids:
        assert len(session_id) == url_safe_session_id_length

    return iter(session_ids)


@pytest.fixture(scope="function")
def uuid_generator() -> Iterator[str]:
    """
    Generates a sequence of predefined UUIDs.

    Can be used max 1 time per test, currently sufficient for all test scenarios.

    Yields:
        str: The next UUID from the predefined list.
    """
    uuids = "1b4a1b7a-dbd6-4be4-a52e-80fdd9ddbfb0"

    return iter(uuids)


@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    Provides a FastAPI test client.

    The test client is initialized once per test session (`scope="session"`)
    and allows making HTTP requests to the FastAPI application instance
    without running a server.

    Returns:
        fastapi.testclient.TestClient: The FastAPI test client.
    """
    return TestClient(app)
