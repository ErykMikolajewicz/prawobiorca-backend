import re
from io import BytesIO

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTPage, LTTextContainer

from app.domain.value_objects.regulations import Chapter, Paragraph, Point, RegulationAct

CHAPTER_CORE = r"^Rozdział\s+(?P<ch_num>[IVX]+)\s+[–-]\s+(?P<ch_title>[^\n]+)"
CHAPTER_PLAIN = r"^Rozdział\s+[IVX]+\s+[–-]\s+.+$"
CHAPTER_BLOCK = rf"{CHAPTER_CORE}\n(?P<ch_body>.*?)(?={CHAPTER_PLAIN}|\Z)"

PARAGRAPH_CORE = r"^§\s+(?P<p_num>\d+)\.\s+(?P<p_title>[^\n]+)"
PARAGRAPH_PLAIN = r"§\s+\d+\.\s+[^\n]+$"
PARAGRAPH_BLOCK = rf"{PARAGRAPH_CORE}\n(?P<p_body>.*?)(?={PARAGRAPH_PLAIN}|\Z)"

POINT_CORE = r"^(?P<pt_num>\d+)[.].*?"
POINT_PLAIN = r"\n\d+[.]\s+.*?"
POINT_BLOCK = rf"{POINT_CORE}\s+(?P<pt_body>.*?)(?={POINT_PLAIN}|\Z)"

FLAGS = re.MULTILINE | re.DOTALL


def extract_document(document_content: bytes, document_title: str) -> RegulationAct:
    def _roman_to_int(roman: str) -> int:
        vals = {"I": 1, "V": 5, "X": 10}
        roman.replace("IV", "IIII")
        roman.replace("IX", "XVIIII")

        return sum([vals[num] for num in roman])

    text = extract_text(document_content)

    chapters = re.finditer(CHAPTER_BLOCK, text, FLAGS)

    chapter_items: list[Chapter] = []

    for chapter in chapters:
        ch_body = chapter.group("ch_body")

        paragraphs = re.finditer(PARAGRAPH_BLOCK, ch_body, FLAGS)

        paragraph_items: list[Paragraph] = []

        for paragraph in paragraphs:
            p_body = paragraph.group("p_body")
            p_num = paragraph.group("p_num")
            p_title = paragraph.group("p_title")

            paragraph = Paragraph(title=p_title, number=int(p_num), points=[])

            paragraph_items.append(paragraph)

            points = re.finditer(POINT_BLOCK, p_body, FLAGS)

            point_items: list[Point] = []

            for point in points:
                pt_number = point.group("pt_num")
                pt_body = point.group("pt_body").replace("\n", "").rstrip()

                point = Point(number=int(pt_number), body=pt_body)

                point_items.append(point)

            paragraph.points = point_items

        if paragraph_items:
            ch_num = chapter.group("ch_num")
            ch_title = chapter.group("ch_title").rstrip()
            chapter = Chapter(title=ch_title, number=_roman_to_int(ch_num), paragraphs=paragraph_items)
            chapter_items.append(chapter)

    return RegulationAct(name=document_title, _chapters=chapter_items)


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
