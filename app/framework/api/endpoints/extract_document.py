import logging
import re

from fastapi import APIRouter
from app.application.use_cases.extraction import extract_text
from pathlib import Path

import re
import os

from app.application.use_cases.extraction import extract_text

from dotenv import load_dotenv
from pathlib import Path


def _extract_document()->list:
    load_dotenv()
    doc_path = Path(os.environ['PWR_REGULAMIN_PDF_URL'])
    doc_str = extract_text(doc_path)
    chapters = []
    
    # pattern for selecting the whole chapter (Rozdział) - header & content
    regex = r"^(?:Rozdział\s)?[IVX]+[^\.\n]*\n[\s\S]*?(?=^(?:Rozdział\s)?[IVX]+[^\.\n]*|\Z)"

    matches = re.finditer(regex, doc_str, re.MULTILINE)
    chapters = [match.group() for match in matches]

    return chapters

logger = logging.getLogger(__name__)

extract_document_router = APIRouter(
    prefix="/test",
    tags=["test"],
)

@extract_document_router.get('/extract_document')
async def extract_document()->list:
    return _extract_document()