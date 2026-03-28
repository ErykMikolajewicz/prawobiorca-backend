from collections.abc import Iterable

from httpx import AsyncClient

from app.domain.value_objects.regulations import RegulationElement


class RegulationSplitter:
    def __init__(self, client: AsyncClient, texts_transformator_url: str):
        self._client = client
        self._split_url = f"{texts_transformator_url}/parse-regulation"

    async def split(self, regulation: bytes) -> Iterable[RegulationElement]:
        response = await self._client.post(self._split_url, timeout=300, files={"file": ("regulation.pdf", regulation)})
        response.raise_for_status()

        return [
            RegulationElement(label=item["label"], text=item["text"], tokens_number=item["tokens_number"])
            for item in response.json()
        ]
