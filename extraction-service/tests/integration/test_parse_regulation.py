import json
from http import HTTPStatus
from pathlib import Path

import httpx2

from tests.consts import EXTRACTION_SERVICE_PORT

DATA_DIR = Path(__file__).parents[1] / "data"
PDF_PATH = DATA_DIR / "pwr-regulamin_2025_slice_7-9.pdf"
EXPECTED_RESPONSE_PATH = DATA_DIR / "pwr-regulamin_2025_slice_7-9.json"


def test_parse_regulation(extraction_service_container):
    url = (
        f"http://{extraction_service_container.get_container_host_ip()}:"
        f"{extraction_service_container.get_exposed_port(EXTRACTION_SERVICE_PORT)}/parse-regulation"
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
