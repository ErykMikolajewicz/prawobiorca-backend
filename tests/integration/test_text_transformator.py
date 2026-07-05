import json
from http import HTTPStatus
from pathlib import Path

import httpx2
import pytest

from tests.consts import TEXT_TRANSFORMATOR_PORT

DATA_DIR = Path(__file__).parents[1] / "data"
PDF_PATH = DATA_DIR / "pwr-regulamin_2025_slice_7-9.pdf"
EXPECTED_RESPONSE_PATH = DATA_DIR / "pwr-regulamin_2025_slice_7-9.json"


@pytest.mark.slow
def test_parse_regulation(text_transformator_container):
    url = (
        f"http://{text_transformator_container.get_container_host_ip()}:"
        f"{text_transformator_container.get_exposed_port(TEXT_TRANSFORMATOR_PORT)}/parse-regulation"
    )

    with PDF_PATH.open("rb") as pdf_file:
        response = httpx2.post(
            url,
            files={
                "file": (
                    PDF_PATH.name,
                    pdf_file,
                    "application/pdf",
                )
            },
            timeout=1500,
        )

    assert response.status_code == HTTPStatus.OK

    parsed_regulation = response.json()
    expected_regulation = json.loads(EXPECTED_RESPONSE_PATH.read_text(encoding="utf-8"))

    assert parsed_regulation == expected_regulation


@pytest.mark.slow
def test_embed_texts(text_transformator_container):
    url = (
        f"http://{text_transformator_container.get_container_host_ip()}:"
        f"{text_transformator_container.get_exposed_port(TEXT_TRANSFORMATOR_PORT)}/embed"
    )

    texts_to_embed = (
        "task: search result | query: akademik politechniki",
        "title: Regulamin | text: Student ma prawo do zakwaterowania w domu studenckim.",
    )

    response = httpx2.post(
        url,
        json=texts_to_embed,
        timeout=1500,
    )

    assert response.status_code == HTTPStatus.OK

    embeddings = response.json()

    assert len(embeddings) == len(texts_to_embed)
    assert all(isinstance(embedding, list) for embedding in embeddings)
    assert all(embedding for embedding in embeddings)
    assert len({len(embedding) for embedding in embeddings}) == 1
    assert all(isinstance(value, float) for embedding in embeddings for value in embedding)
