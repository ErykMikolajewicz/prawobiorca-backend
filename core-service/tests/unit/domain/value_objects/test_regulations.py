import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.domain.value_objects import regulations as regulations_module
from src.domain.value_objects.legal_units import RegulationElement, UnitType, UsefulLabels
from src.domain.value_objects.regulations import RegulationAct

DATA_DIR = Path(__file__).parents[3] / "data"

ACT_FIXTURE = "ustawa-nauka_slice_30-31"

DESIRED_TOKENS_LENGTH = 60
TITLE_TOKENS_OVERHEAD = 4


class WordTokenizer:
    def count_tokens(self, text: str) -> int:
        return len(text.split())


@pytest.fixture(autouse=True)
def token_settings():
    with (
        patch.object(
            regulations_module,
            "app_settings",
            SimpleNamespace(DOCUMENT_DESIRED_TOKENS_LENGTH=DESIRED_TOKENS_LENGTH),
        ),
        patch.object(
            regulations_module,
            "tokenizer_settings",
            SimpleNamespace(MAX_TOKENS=2048, MAX_TITLE_TOKENS_OVERHEAD=TITLE_TOKENS_OVERHEAD),
        ),
    ):
        yield


def load_regulation_elements(regulation_name: str) -> list[RegulationElement]:
    raw_elements = json.loads((DATA_DIR / f"{regulation_name}.json").read_text(encoding="utf-8"))

    return [RegulationElement(label=element["label"], text=element["text"]) for element in raw_elements]


def create_documents(elements: list[RegulationElement]) -> list:
    collection = RegulationAct(elements, WordTokenizer()).get_documents_to_embed()

    return sorted(collection, key=lambda document: document.chunk_order)


def create_subsections(subsections_count: int, words_per_subsection: int) -> list[RegulationElement]:
    elements = [RegulationElement(label=UsefulLabels.TEXT, text="Art. 110. 1. Studenci tworzą samorząd studencki.")]
    for subsection_number in range(2, subsections_count + 1):
        text = f"{subsection_number}. " + " ".join(["słowo"] * words_per_subsection)
        elements.append(RegulationElement(label=UsefulLabels.LIST_ITEM, text=text))

    return elements


def test_each_article_becomes_separate_document():
    documents = create_documents(load_regulation_elements(ACT_FIXTURE))

    article_numbers = [document.unit_number for document in documents if document.unit_type == UnitType.ARTICLE]

    assert sorted(set(article_numbers), key=int) == [
        "107",
        "108",
        "109",
        "110",
        "111",
        "112",
        "113",
        "114",
        "115",
        "116",
    ]


def test_short_articles_are_not_merged_together():
    documents = create_documents(load_regulation_elements(ACT_FIXTURE))

    short_article = next(document for document in documents if document.unit_number == "112")

    assert short_article.parts_total == 1
    assert "Art. 113" not in short_article.text
    assert "Nauczycielem akademickim" not in short_article.text


def test_documents_carry_unit_metadata():
    documents = create_documents(load_regulation_elements(ACT_FIXTURE))

    document = next(document for document in documents if document.unit_number == "112")

    assert document.unit_type == UnitType.ARTICLE
    assert document.unit_path == ["Rozdział 5 Pracownicy uczelni"]
    assert document.title == "Rozdział 5 Pracownicy uczelni > Art. 112"
    assert document.part_index == 1


def test_long_unit_is_split_on_subsection_boundaries():
    elements = create_subsections(subsections_count=6, words_per_subsection=25)

    documents = create_documents(elements)

    assert len(documents) > 1
    for document in documents:
        assert document.text.split(" ")[0].endswith(".")
        assert document.parts_total == len(documents)


def test_split_unit_keeps_whole_content():
    elements = create_subsections(subsections_count=6, words_per_subsection=25)

    documents = create_documents(elements)

    joined_text = " ".join(document.text for document in documents)
    assert joined_text.startswith("1. Studenci tworzą samorząd studencki.")
    assert joined_text.count("2.") == 1
    assert joined_text.count("6.") == 1


def test_part_titles_are_unique_within_unit():
    elements = create_subsections(subsections_count=6, words_per_subsection=25)

    documents = create_documents(elements)

    titles = [document.title for document in documents]
    assert len(set(titles)) == len(titles)
    assert titles[0].startswith("Art. 110 ust.")


def test_part_titles_use_part_numbers_when_subsections_repeat():
    long_point = " ".join(["słowo"] * 25)
    elements = [
        RegulationElement(label=UsefulLabels.TEXT, text="Art. 110. 1. Studenci tworzą samorząd w zakresie:"),
        RegulationElement(label=UsefulLabels.LIST_ITEM, text=f"1) {long_point};"),
        RegulationElement(label=UsefulLabels.LIST_ITEM, text=f"2) {long_point};"),
        RegulationElement(label=UsefulLabels.LIST_ITEM, text=f"3) {long_point}."),
    ]

    documents = create_documents(elements)

    assert len(documents) > 1
    assert all("(część" in document.title for document in documents)


def test_element_longer_than_budget_is_split_by_sentences():
    sentence = " ".join(["słowo"] * 30)
    elements = [RegulationElement(label=UsefulLabels.TEXT, text=f"Art. 110. {sentence}. {sentence}. {sentence}.")]

    documents = create_documents(elements)

    assert len(documents) == 3
    for document in documents:
        assert len(document.text.split(" ")) <= DESIRED_TOKENS_LENGTH


def test_element_without_sentence_boundaries_is_split_by_tokens():
    elements = [RegulationElement(label=UsefulLabels.TEXT, text="Art. 110. " + " ".join(["słowo"] * 200))]

    documents = create_documents(elements)

    assert len(documents) > 1
    for document in documents:
        assert len(document.text.split(" ")) <= DESIRED_TOKENS_LENGTH


def test_too_long_breadcrumb_is_trimmed_from_the_top():
    elements = [
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="DZIAŁ VII"),
        RegulationElement(
            label=UsefulLabels.SECTION_HEADER,
            text="Bardzo długi tytuł działu o studiach i studentach oraz sprawach im podobnych",
        ),
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="Rozdział 4"),
        RegulationElement(
            label=UsefulLabels.SECTION_HEADER, text="Samorząd studencki i organizacje studenckie w uczelni"
        ),
        RegulationElement(label=UsefulLabels.TEXT, text="Art. 110. Studenci tworzą samorząd."),
    ]

    documents = create_documents(elements)

    assert "DZIAŁ VII" not in documents[0].title
    assert documents[0].title.endswith("Art. 110")
    assert documents[0].unit_path == [
        "DZIAŁ VII Bardzo długi tytuł działu o studiach i studentach oraz sprawach im podobnych",
        "Rozdział 4 Samorząd studencki i organizacje studenckie w uczelni",
    ]


def test_elements_are_joined_with_separator():
    documents = create_documents(load_regulation_elements(ACT_FIXTURE))

    article = next(document for document in documents if document.unit_number == "108")

    assert "studiów; 2) rezygnacji" in article.text
    assert "studiów;2)" not in article.text


def test_unnumbered_content_has_no_title():
    elements = [RegulationElement(label=UsefulLabels.TEXT, text="7. Podmiot zapewnia przebieg akcji protestacyjnej.")]

    documents = create_documents(elements)

    assert documents[0].title is None
    assert documents[0].unit_type == UnitType.UNNUMBERED


def test_chunk_order_is_continuous():
    documents = create_documents(load_regulation_elements(ACT_FIXTURE))

    assert [document.chunk_order for document in documents] == list(range(len(documents)))


def test_unit_with_title_but_without_content_produces_no_documents():
    elements = [RegulationElement(label=UsefulLabels.SECTION_HEADER, text="§ 5 . Systemy komunikacji")]

    documents = create_documents(elements)

    assert documents == []
