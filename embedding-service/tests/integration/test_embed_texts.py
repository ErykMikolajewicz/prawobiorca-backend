from http import HTTPStatus

import httpx2

from tests.consts import EMBEDDING_SERVICE_PORT


def test_embed_texts(embedding_service_container):
    url = (
        f"http://{embedding_service_container.get_container_host_ip()}:"
        f"{embedding_service_container.get_exposed_port(EMBEDDING_SERVICE_PORT)}/embed"
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
