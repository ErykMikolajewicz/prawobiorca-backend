import pytest

from app.application.dtos.account import LoginData


@pytest.fixture
def login_data():
    return LoginData(username="example@example.com", password="StrongPassword3!")
