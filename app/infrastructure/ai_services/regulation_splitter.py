from collections.abc import Iterable

from httpx2 import AsyncClient

from app.domain.value_objects.regulations import RegulationElement


class RegulationSplitter:
    def __init__(self, client: AsyncClient, extraction_service_url: str):
        self._client = client
        self._split_url = f"{extraction_service_url}/parse-regulation"

    async def split(self, regulation: bytes) -> Iterable[RegulationElement]:
        response = await self._client.post(
            self._split_url, timeout=1500, files={"file": ("regulation.pdf", regulation)}
        )

        return [RegulationElement(label=item["label"], text=item["text"]) for item in response.json()]
