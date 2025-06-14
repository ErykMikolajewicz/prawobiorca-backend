import pytest

from app.infrastructure.utilities.security import url_safe_bearer_token_length


@pytest.fixture
def bearer_token_generator():
    def get_token():
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
def uuid_generator():
    def get_uuid():
        uuids = (
            "1b4a1b7a-dbd6-4be4-a52e-80fdd9ddbfb0",
            "ad987bb3-cf5b-4d07-a23c-2e5f1221171a",
            "4596f6de-d067-4e36-ad9f-a3b3959eee6b",
        )
        for uuid_ in uuids:
            yield uuid_

    return get_uuid()
