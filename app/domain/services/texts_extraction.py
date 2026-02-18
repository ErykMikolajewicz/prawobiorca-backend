import re
from io import BytesIO

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTPage, LTTextContainer


def divide_document(document: bytes) -> list:
    doc_str = extract_text(document)

    # pattern for selecting the whole chapter (Rozdział) - header & content
    regex_chapter = r"^(?:Rozdział\s)?[IVX]+[^\.\n]*\n[\s\S]*?(?=^(?:Rozdział\s)?[IVX]+[^\.\n]*|\Z)"

    # pattern for selecting only the title of the chapter - e.g. "Rozdział I – Postanowienia ogólne"
    regex_chapter_title = r"^Rozdział\s[IVX]+[^\.\n§]* "

    matches = re.finditer(regex_chapter, doc_str, re.MULTILINE)
    chapters = [match.group() for match in matches]

    chapter_titles = [str(re.findall(regex_chapter_title, chapter)[0]).strip() or "" for chapter in chapters]
    pure_chapter_titles = []

    # formatting list elements to tuple (chapter num, chapter title, contents)
    for i, chapter_title in enumerate(chapter_titles, start=1):
        pure_title_regex = r"[-–]\s*(.+)"
        match = re.search(pure_title_regex, chapter_title)

        if not match:
            raise Exception("Rozdział XXX regex error")

        pure_title = match.group(1).strip()

        pure_chapter_titles.append([i, pure_title])

    structured_chapters = [pure_chapter_titles[i] + [chapters[i]] for i in range(len(chapters))]

    regex_remove_chapter_name = r"(?s)^.*?\n\s*§\s*"

    paragraph_groups_regex = r"(?s)(?P<title>§\s+\d+\.\s+.*?\n)(?P<contents>.*?)(?=§\s+\d+\.|\Z)"

    for i, (nr, title, content) in enumerate(structured_chapters):
        new_content = re.sub(regex_remove_chapter_name, "§", content)

        paragraphs = []
        for match in list(re.finditer(paragraph_groups_regex, new_content, re.DOTALL | re.MULTILINE)):
            paragraph = (match.group("title").replace("\n", "").strip(), match.group("contents"))
            paragraphs.append(paragraph)

        structured_chapters[i] = (nr, title, paragraphs)

    return structured_chapters


def extract_text(pdf_bytes: bytes, top_margin: float = 50, bottom_margin: float = 60) -> str:
    text = ""
    with BytesIO(pdf_bytes) as fp:
        for page_layout in extract_pages(fp):
            if isinstance(page_layout, LTPage):
                page_height = page_layout.height
                for element in page_layout:
                    if isinstance(element, LTTextContainer):
                        if element.y1 < page_height - top_margin and element.y0 > bottom_margin:
                            text += element.get_text()
    return text
