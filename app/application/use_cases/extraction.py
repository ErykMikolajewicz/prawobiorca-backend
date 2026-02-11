import re
from pathlib import Path

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTPage, LTTextContainer


def extract_text(pdf_path: Path, top_margin=50, bottom_margin=60) -> str:
    text = ""
    for page_layout in extract_pages(pdf_path):
        if isinstance(page_layout, LTPage):
            page_height = page_layout.height
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    if element.y1 < page_height - top_margin and element.y0 > bottom_margin:
                        text += element.get_text()
    return text


def extract_articles(act_text: str) -> list[str]:
    pattern = r"\n(?![ARD])"
    act_text = re.sub(pattern, " ", act_text)

    pattern = r"(\nArt\. \d+(?:[a-z])*\. )"

    articles_text = re.split(pattern, act_text)
    articles_text.pop(0)  # To remove text before first article

    articles = []
    for i, article_text in enumerate(articles_text):
        if i % 2 == 0:
            continue
        articles.append(article_text)

    for i, article in enumerate(articles):
        if article.count("\n") > 0:
            new_line_index = article.index("\n")
            articles[i] = article[:new_line_index]

    articles = [
        article for article in articles if (re.search(r"\(uchylony\)", article) is None) or len(article.strip()) > 12
    ]

    for i, article in enumerate(articles):
        articles[i] = re.sub(r"\s+", " ", article).strip()

    return articles
