"""
Pytest configuration file for the FastAPI project.

Contains common fixtures used in tests, such as the FastAPI test client
and generators for tokens and UUIDs.
"""

from collections.abc import Iterator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from main import prawobiorca


@pytest.fixture(scope="function")
def uuid_generator() -> Iterator[UUID]:
    """
    Generates a sequence of predefined UUIDs.

    Can be used max 2 time per test, currently sufficient for all test scenarios.

    Yields:
        str: The next UUID from the predefined list.
    """
    uuids = (UUID("1b4a1b7a-dbd6-4be4-a52e-80fdd9ddbfb0"), UUID("a3f54f36-9653-4ccf-b9f4-81bf885d02ee"))

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
    return TestClient(prawobiorca)
