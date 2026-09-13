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

CHUNK_MAX_TOKENS = 60
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
            SimpleNamespace(CHUNK_MAX_TOKENS=CHUNK_MAX_TOKENS),
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


def create_sections(elements: list[RegulationElement]) -> list:
    collection = RegulationAct(elements, WordTokenizer()).get_sections_to_embed()

    return sorted(collection, key=lambda section: section.section_order)


def create_subsections(subsections_count: int, words_per_subsection: int) -> list[RegulationElement]:
    elements = [RegulationElement(label=UsefulLabels.TEXT, text="Art. 110. 1. Studenci tworzą samorząd studencki.")]
    for subsection_number in range(2, subsections_count + 1):
        text = f"{subsection_number}. " + " ".join(["słowo"] * words_per_subsection)
        elements.append(RegulationElement(label=UsefulLabels.LIST_ITEM, text=text))

    return elements


def test_each_article_becomes_separate_section():
    sections = create_sections(load_regulation_elements(ACT_FIXTURE))

    article_numbers = [section.unit_number for section in sections if section.unit_type == UnitType.ARTICLE]

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
    sections = create_sections(load_regulation_elements(ACT_FIXTURE))

    short_article = next(section for section in sections if section.unit_number == "112")

    assert len(short_article.chunks) == 1
    assert "Art. 113" not in short_article.text
    assert "Nauczycielem akademickim" not in short_article.text


def test_sections_carry_unit_metadata():
    sections = create_sections(load_regulation_elements(ACT_FIXTURE))

    section = next(section for section in sections if section.unit_number == "112")

    assert section.unit_type == UnitType.ARTICLE
    assert section.unit_path == ["Rozdział 5 Pracownicy uczelni"]
    assert section.header == "Rozdział 5 Pracownicy uczelni > Art. 112"


def test_long_section_stays_one_section_split_into_chunks():
    elements = create_subsections(subsections_count=6, words_per_subsection=25)

    sections = create_sections(elements)

    assert len(sections) == 1
    assert len(sections[0].chunks) > 1


def test_section_text_keeps_whole_unit():
    elements = create_subsections(subsections_count=6, words_per_subsection=25)

    section = create_sections(elements)[0]

    assert section.text.startswith("1. Studenci tworzą samorząd studencki.")
    assert section.text.count("2.") == 1
    assert section.text.count("6.") == 1


def test_chunks_are_split_on_subsection_boundaries():
    elements = create_subsections(subsections_count=6, words_per_subsection=25)

    section = create_sections(elements)[0]

    for chunk in section.chunks:
        assert chunk.text.split(" ")[0].endswith(".")


def test_chunks_keep_whole_section_content():
    elements = create_subsections(subsections_count=6, words_per_subsection=25)

    section = create_sections(elements)[0]

    assert " ".join(chunk.text for chunk in section.chunks) == " ".join(section.text.split("\n"))


def test_chunk_titles_are_unique_within_section():
    elements = create_subsections(subsections_count=6, words_per_subsection=25)

    section = create_sections(elements)[0]

    embed_titles = [chunk.embed_title for chunk in section.chunks]
    assert len(set(embed_titles)) == len(embed_titles)
    assert embed_titles[0].startswith("Art. 110 ust.")


def test_chunk_titles_use_part_numbers_when_subsections_repeat():
    long_point = " ".join(["słowo"] * 25)
    elements = [
        RegulationElement(label=UsefulLabels.TEXT, text="Art. 110. 1. Studenci tworzą samorząd w zakresie:"),
        RegulationElement(label=UsefulLabels.LIST_ITEM, text=f"1) {long_point};"),
        RegulationElement(label=UsefulLabels.LIST_ITEM, text=f"2) {long_point};"),
        RegulationElement(label=UsefulLabels.LIST_ITEM, text=f"3) {long_point}."),
    ]

    section = create_sections(elements)[0]

    assert len(section.chunks) > 1
    assert all("(część" in chunk.embed_title for chunk in section.chunks)


def test_section_header_has_no_part_suffix():
    elements = create_subsections(subsections_count=6, words_per_subsection=25)

    section = create_sections(elements)[0]

    assert section.header == "Art. 110"


def test_element_longer_than_budget_is_split_by_sentences():
    sentence = " ".join(["słowo"] * 30)
    elements = [RegulationElement(label=UsefulLabels.TEXT, text=f"Art. 110. {sentence}. {sentence}. {sentence}.")]

    section = create_sections(elements)[0]

    assert len(section.chunks) == 3
    for chunk in section.chunks:
        assert len(chunk.text.split(" ")) <= CHUNK_MAX_TOKENS


def test_element_without_sentence_boundaries_is_split_by_tokens():
    elements = [RegulationElement(label=UsefulLabels.TEXT, text="Art. 110. " + " ".join(["słowo"] * 200))]

    section = create_sections(elements)[0]

    assert len(section.chunks) > 1
    for chunk in section.chunks:
        assert len(chunk.text.split(" ")) <= CHUNK_MAX_TOKENS


def test_too_long_breadcrumb_is_trimmed_only_in_chunk_title():
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

    section = create_sections(elements)[0]

    assert section.header.startswith("DZIAŁ VII")
    assert section.header.endswith("Art. 110")
    assert "DZIAŁ VII" not in section.chunks[0].embed_title
    assert section.chunks[0].embed_title.endswith("Art. 110")
    assert section.unit_path == [
        "DZIAŁ VII Bardzo długi tytuł działu o studiach i studentach oraz sprawach im podobnych",
        "Rozdział 4 Samorząd studencki i organizacje studenckie w uczelni",
    ]


def test_elements_are_joined_with_separator():
    sections = create_sections(load_regulation_elements(ACT_FIXTURE))

    article = next(section for section in sections if section.unit_number == "108")

    assert "studiów;\n2) rezygnacji" in article.text
    assert "studiów;2)" not in article.text


def test_unnumbered_content_has_no_header():
    elements = [RegulationElement(label=UsefulLabels.TEXT, text="7. Podmiot zapewnia przebieg akcji protestacyjnej.")]

    sections = create_sections(elements)

    assert sections[0].header is None
    assert sections[0].unit_type == UnitType.UNNUMBERED


def test_section_order_is_continuous():
    sections = create_sections(load_regulation_elements(ACT_FIXTURE))

    assert [section.section_order for section in sections] == list(range(len(sections)))


def test_chunk_index_is_continuous_within_section():
    elements = create_subsections(subsections_count=6, words_per_subsection=25)

    section = create_sections(elements)[0]

    assert [chunk.chunk_index for chunk in section.chunks] == list(range(len(section.chunks)))


def test_unit_with_title_but_without_content_produces_no_sections():
    elements = [RegulationElement(label=UsefulLabels.SECTION_HEADER, text="§ 5 . Systemy komunikacji")]

    sections = create_sections(elements)

    assert sections == []
