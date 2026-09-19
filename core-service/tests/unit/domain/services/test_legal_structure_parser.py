import json
from pathlib import Path

import pytest

from src.domain.services.legal_structure_parser import LegalStructureParser
from src.domain.value_objects.legal_units import RegulationElement, UnitType, UsefulLabels

DATA_DIR = Path(__file__).parents[3] / "data"

ACT_FIXTURE = "ustawa-nauka_slice_30-31"
STATUTE_FIXTURE = "pwr-regulamin_2025_slice_7-9"
PROMOTION_DATABASE_FIXTURE = "ustawa-nauka_slice_209-210"


def load_regulation_elements(regulation_name: str) -> list[RegulationElement]:
    raw_elements = json.loads((DATA_DIR / f"{regulation_name}.json").read_text(encoding="utf-8"))

    return [RegulationElement(label=element["label"], text=element["text"]) for element in raw_elements]


def unit_text(unit) -> str:
    return " ".join(element.text for element in unit.elements)


def test_act_is_split_into_separate_articles():
    elements = load_regulation_elements(ACT_FIXTURE)

    units = LegalStructureParser().parse(elements)

    article_numbers = [unit.number for unit in units if unit.unit_type == UnitType.ARTICLE]
    assert article_numbers == ["107", "108", "109", "110", "111", "112", "113", "114", "115", "116"]


def test_article_keeps_division_breadcrumb():
    elements = load_regulation_elements(ACT_FIXTURE)

    units = LegalStructureParser().parse(elements)

    article = next(unit for unit in units if unit.number == "110")
    assert article.path == ["Rozdział 4 Samorząd studencki i organizacje studenckie"]
    assert article.breadcrumb == "Rozdział 4 Samorząd studencki i organizacje studenckie > Art. 110"


def test_articles_do_not_leak_into_each_other():
    elements = load_regulation_elements(ACT_FIXTURE)

    units = LegalStructureParser().parse(elements)

    article = next(unit for unit in units if unit.number == "108")
    assert unit_text(article).startswith("1. Studenta skreśla się z listy studentów")
    assert unit_text(article).endswith("3. Skreślenie z listy studentów następuje w drodze decyzji administracyjnej.")
    assert "Art. 109" not in unit_text(article)


def test_statute_is_split_into_paragraphs_with_titles():
    elements = load_regulation_elements(STATUTE_FIXTURE)

    units = LegalStructureParser().parse(elements)

    paragraphs = [unit for unit in units if unit.unit_type == UnitType.PARAGRAPH]
    assert [unit.number for unit in paragraphs] == ["5", "6", "7"]
    assert paragraphs[1].title == "Prawa studenta"
    assert paragraphs[1].breadcrumb == "Rozdział II Prawa i obowiązki studenta > § 6 Prawa studenta"


def test_page_headers_and_footers_are_dropped():
    elements = load_regulation_elements(ACT_FIXTURE) + load_regulation_elements(STATUTE_FIXTURE)

    units = LegalStructureParser().parse(elements)

    parsed_text = " ".join(unit_text(unit) for unit in units)
    assert "Dziennik Ustaw" not in parsed_text
    assert "Strona 7 z 48" not in parsed_text


def test_elements_before_first_unit_become_unnumbered_unit():
    elements = load_regulation_elements(ACT_FIXTURE)

    units = LegalStructureParser().parse(elements)

    assert units[0].unit_type == UnitType.UNNUMBERED
    assert units[0].number is None
    assert unit_text(units[0]).startswith("7. Podmiot, o którym mowa w ust. 2")


def test_article_reference_inside_text_does_not_start_new_unit():
    elements = [
        RegulationElement(label=UsefulLabels.TEXT, text="Art. 109. Osoba zachowuje prawa studenta."),
        RegulationElement(label=UsefulLabels.TEXT, text="Przepisy art. 110 ust. 8 zdanie drugie stosuje się."),
    ]

    units = LegalStructureParser().parse(elements)

    assert len(units) == 1
    assert units[0].number == "109"
    assert len(units[0].elements) == 2


def test_glued_articles_are_split_into_separate_units():
    elements = [
        RegulationElement(
            label=UsefulLabels.TEXT,
            text="Art. 112. Pracownikami uczelni są nauczyciele. Art. 113. Nauczycielem może być osoba.",
        )
    ]

    units = LegalStructureParser().parse(elements)

    assert [unit.number for unit in units] == ["112", "113"]


def test_text_is_normalized():
    elements = [
        RegulationElement(
            label=UsefulLabels.TEXT,
            text="Art. 5. 1. Uczelnia,  oprócz  systemu , udostępnia konto ( § 27 ) studentowi .",
        )
    ]

    units = LegalStructureParser().parse(elements)

    assert unit_text(units[0]) == "1. Uczelnia, oprócz systemu, udostępnia konto (§ 27) studentowi."


def test_paragraph_is_treated_as_content_when_act_uses_articles():
    elements = [
        RegulationElement(label=UsefulLabels.TEXT, text="Art. 5. § 1. Odpowiedzialności karnej podlega sprawca."),
        RegulationElement(label=UsefulLabels.TEXT, text="§ 2. Przepisu § 1 nie stosuje się."),
    ]

    units = LegalStructureParser().parse(elements)

    assert len(units) == 1
    assert units[0].unit_type == UnitType.ARTICLE
    assert units[0].number == "5"
    assert len(units[0].elements) == 2


def test_points_labelled_as_headers_stay_in_article():
    elements = load_regulation_elements(PROMOTION_DATABASE_FIXTURE)

    units = LegalStructureParser().parse(elements)

    article = next(unit for unit in units if unit.number == "349")
    article_texts = [element.text for element in article.elements]
    assert "1) imiona i nazwisko;" in article_texts
    assert "<1a) stopień albo tytuł profesora;" in article_texts
    assert "5) informacje o wzorach:" in article_texts
    assert units[-1] is article


def test_points_labelled_as_headers_inherit_subsection():
    elements = load_regulation_elements(PROMOTION_DATABASE_FIXTURE)

    units = LegalStructureParser().parse(elements)

    article = next(unit for unit in units if unit.number == "349")
    point = next(element for element in article.elements if element.text.startswith("<3a)"))
    assert point.subsection == "1"


def test_letter_labelled_as_header_is_content():
    elements = [
        RegulationElement(label=UsefulLabels.TEXT, text="Art. 5. 1. Baza obejmuje:"),
        RegulationElement(label=UsefulLabels.LIST_ITEM, text="1) informacje o wzorach:"),
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="a) dyplomów ukończenia studiów,"),
    ]

    units = LegalStructureParser().parse(elements)

    assert len(units) == 1
    assert len(units[0].elements) == 3
    assert units[0].path == []


def test_nested_divisions_build_full_path():
    elements = [
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="DZIAŁ VII"),
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="Studia i studenci"),
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="Rozdział 4"),
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="Samorząd studencki"),
        RegulationElement(label=UsefulLabels.TEXT, text="Art. 110. 1. Studenci tworzą samorząd."),
    ]

    units = LegalStructureParser().parse(elements)

    assert units[0].path == ["DZIAŁ VII Studia i studenci", "Rozdział 4 Samorząd studencki"]


def test_division_of_the_same_rank_replaces_previous_one():
    elements = [
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="Rozdział 4"),
        RegulationElement(label=UsefulLabels.TEXT, text="Art. 110. Studenci tworzą samorząd."),
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="Rozdział 5"),
        RegulationElement(label=UsefulLabels.TEXT, text="Art. 112. Pracownikami uczelni są nauczyciele."),
    ]

    units = LegalStructureParser().parse(elements)

    assert units[0].path == ["Rozdział 4"]
    assert units[1].path == ["Rozdział 5"]


def test_header_without_division_keyword_becomes_path_segment():
    elements = [
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="Postanowienia ogólne"),
        RegulationElement(label=UsefulLabels.TEXT, text="Uczelnia działa na podstawie ustawy."),
    ]

    units = LegalStructureParser().parse(elements)

    assert units[0].unit_type == UnitType.UNNUMBERED
    assert units[0].path == ["Postanowienia ogólne"]


def test_points_inherit_subsection_of_their_parent():
    elements = load_regulation_elements(ACT_FIXTURE)

    units = LegalStructureParser().parse(elements)

    article = next(unit for unit in units if unit.number == "107")
    assert [element.subsection for element in article.elements] == ["1", "2", "2", "2"]


@pytest.mark.parametrize("empty_text", ["", "   "])
def test_empty_elements_are_dropped(empty_text):
    elements = [
        RegulationElement(label=UsefulLabels.TEXT, text="Art. 1. Przepis."),
        RegulationElement(label=UsefulLabels.TEXT, text=empty_text),
    ]

    units = LegalStructureParser().parse(elements)

    assert len(units[0].elements) == 1


def test_unit_without_content_is_dropped():
    elements = [RegulationElement(label=UsefulLabels.SECTION_HEADER, text="Rozdział 4")]

    units = LegalStructureParser().parse(elements)

    assert units == []


def test_unnumbered_unit_without_divisions_has_no_breadcrumb():
    elements = [RegulationElement(label=UsefulLabels.TEXT, text="7. Podmiot zapewnia przebieg akcji.")]

    units = LegalStructureParser().parse(elements)

    assert units[0].breadcrumb is None
    assert units[0].citation is None


def test_unit_marker_placed_after_header_title_starts_unit():
    elements = [
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="Obowiązki mieszkańca domu studenckiego § 2"),
        RegulationElement(label=UsefulLabels.TEXT, text="Mieszkaniec domu studenckiego ma obowiązek:"),
    ]

    units = LegalStructureParser().parse(elements)

    assert len(units) == 1
    assert units[0].unit_type == UnitType.PARAGRAPH
    assert units[0].number == "2"
    assert units[0].title == "Obowiązki mieszkańca domu studenckiego"
    assert units[0].path == []


def test_header_above_bare_unit_marker_becomes_unit_title():
    elements = [
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="Prawa mieszkańca domu studenckiego"),
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="§ 1"),
        RegulationElement(label=UsefulLabels.TEXT, text="Mieszkaniec domu studenckiego ma prawo do:"),
    ]

    units = LegalStructureParser().parse(elements)

    assert len(units) == 1
    assert units[0].number == "1"
    assert units[0].title == "Prawa mieszkańca domu studenckiego"
    assert units[0].breadcrumb == "§ 1 Prawa mieszkańca domu studenckiego"


def test_division_title_is_not_stolen_by_following_unit():
    elements = [
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="Rozdział 4"),
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="Samorząd studencki"),
        RegulationElement(label=UsefulLabels.TEXT, text="Art. 110. Studenci tworzą samorząd."),
    ]

    units = LegalStructureParser().parse(elements)

    assert units[0].title is None
    assert units[0].path == ["Rozdział 4 Samorząd studencki"]
