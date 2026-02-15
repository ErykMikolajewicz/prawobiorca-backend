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

def _divide_document()->list:
    """Returns a list of chapters of the document"""
    load_dotenv()
    doc_path = Path(os.environ['PWR_REGULAMIN_PDF_URL'])
    doc_str = extract_text(doc_path)
    chapters = []
    
    # pattern for selecting the whole chapter (Rozdział) - header & content
    regex_chapter = r"^(?:Rozdział\s)?[IVX]+[^\.\n]*\n[\s\S]*?(?=^(?:Rozdział\s)?[IVX]+[^\.\n]*|\Z)"
    
    # pattern for selecting only the title of the chapter - e.g. "Rozdział I – Postanowienia ogólne"
    regex_chapter_title = r"^Rozdział\s[IVX]+[^\.\n§]* "

    matches = re.finditer(regex_chapter, doc_str, re.MULTILINE)
    chapters = [match.group() for match in matches]

    chapter_titles = [str(re.findall(regex_chapter_title, chapter)[0]).strip() or '' for chapter in chapters]
    pure_chapter_titles = []
    
    for i, chapter_title in enumerate(chapter_titles, start=1):
        print(i, chapter_title)
        pure_title_regex = r'[-–]\s*(.+)'
        match = re.search(pure_title_regex, chapter_title)
        
        if not match:
            raise Exception("Rozdział XXX regex error")
        
        pure_title = match.group(1).strip()
            
        pure_chapter_titles.append([i, pure_title]) 
  
    return [pure_chapter_titles[i]+[chapters[i]] for i in range(len(chapters))]

logger = logging.getLogger(__name__)

divide_document_router = APIRouter(
    prefix="/test",
    tags=["test"],
)

@divide_document_router.get('/divide_document')
async def divide_document()->list:
    return _divide_document()