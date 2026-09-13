import re
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from src.domain.services.legal_structure_parser import LegalStructureParser
from src.domain.value_objects.legal_units import (
    BREADCRUMB_SEPARATOR,
    LegalUnit,
    LegalUnitElement,
    RegulationElement,
)
from src.domain.value_objects.sections import RegulationSection, SectionChunk, SectionsCollection
from src.shared.settings.application import app_settings
from src.shared.settings.tokenizer import tokenizer_settings

SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.;])\s+")

MIN_CONTENT_TOKENS = 32

MAX_TITLE_TOKENS_SHARE = 0.25


class Tokenizer(Protocol):
    def count_tokens(self, text: str) -> int: ...


@dataclass
class RegulationAct:
    _elements: Iterable[RegulationElement]
    _tokenizer: Tokenizer

    def get_sections_to_embed(self) -> SectionsCollection:
        units = LegalStructureParser().parse(self._elements)

        sections = []
        for unit in units:
            section = self._create_section(unit)
            if section is not None:
                sections.append(section)

        for index, section in enumerate(sections):
            section.section_order = index

        return SectionsCollection(sections)

    def _create_section(self, unit: LegalUnit) -> RegulationSection | None:
        if not unit.elements:
            return None

        embed_title = self._fit_title(unit)
        content_budget = self._count_content_budget(embed_title)
        parts = self._split_to_parts(unit.elements, content_budget)
        part_titles = self._create_part_titles(embed_title, parts)

        chunks = [
            SectionChunk(
                text=" ".join(element.text for element in part),
                embed_title=part_title,
                chunk_index=chunk_index,
            )
            for chunk_index, (part, part_title) in enumerate(zip(parts, part_titles, strict=True))
        ]

        return RegulationSection(
            header=unit.breadcrumb,
            text="\n".join(element.text for element in unit.elements),
            chunks=chunks,
            unit_type=unit.unit_type,
            unit_number=unit.number,
            unit_path=list(unit.path),
        )

    def _fit_title(self, unit: LegalUnit) -> str | None:
        segments = unit.breadcrumb_segments
        if not segments:
            return None

        max_title_tokens = int(app_settings.CHUNK_MAX_TOKENS * MAX_TITLE_TOKENS_SHARE)
        title = BREADCRUMB_SEPARATOR.join(segments)
        while len(segments) > 1 and self._tokenizer.count_tokens(title) > max_title_tokens:
            segments = segments[1:]
            title = BREADCRUMB_SEPARATOR.join(segments)

        return title

    def _count_content_budget(self, title: str | None) -> int:
        title_tokens = self._tokenizer.count_tokens(title) if title is not None else 0
        tokens_limit = min(app_settings.CHUNK_MAX_TOKENS, tokenizer_settings.MAX_TOKENS)

        content_budget = tokens_limit - title_tokens - tokenizer_settings.MAX_TITLE_TOKENS_OVERHEAD

        return max(content_budget, MIN_CONTENT_TOKENS)

    def _split_to_parts(self, elements: list[LegalUnitElement], content_budget: int) -> list[list[LegalUnitElement]]:
        atoms = []
        for element in elements:
            atoms.extend(self._split_long_element(element, content_budget))

        parts = []
        current_part = []
        current_tokens = 0
        for atom in atoms:
            atom_tokens = self._tokenizer.count_tokens(atom.text)

            if current_part and current_tokens + atom_tokens > content_budget:
                parts.append(current_part)
                current_part = []
                current_tokens = 0

            current_part.append(atom)
            current_tokens += atom_tokens

        if current_part:
            parts.append(current_part)

        return parts

    def _split_long_element(self, element: LegalUnitElement, content_budget: int) -> list[LegalUnitElement]:
        if self._tokenizer.count_tokens(element.text) <= content_budget:
            return [element]

        fragments = []
        for sentence in SENTENCE_SPLIT_PATTERN.split(element.text):
            fragments.extend(self._split_by_tokens(sentence, content_budget))

        return [LegalUnitElement(text=fragment, subsection=element.subsection) for fragment in fragments]

    def _split_by_tokens(self, text: str, content_budget: int) -> list[str]:
        if self._tokenizer.count_tokens(text) <= content_budget:
            return [text]

        fragments = []
        current_words = []
        current_tokens = 0
        for word in text.split(" "):
            word_tokens = self._tokenizer.count_tokens(word)

            if current_words and current_tokens + word_tokens > content_budget:
                fragments.append(" ".join(current_words))
                current_words = []
                current_tokens = 0

            current_words.append(word)
            current_tokens += word_tokens

        if current_words:
            fragments.append(" ".join(current_words))

        return fragments

    @staticmethod
    def _create_part_titles(title: str | None, parts: list[list[LegalUnitElement]]) -> list[str | None]:
        parts_total = len(parts)
        if parts_total == 1:
            return [title]

        subsection_suffixes = [RegulationAct._create_subsection_suffix(part) for part in parts]
        are_suffixes_unambiguous = None not in subsection_suffixes and len(set(subsection_suffixes)) == parts_total

        part_titles = []
        for part_index, subsection_suffix in enumerate(subsection_suffixes, start=1):
            if are_suffixes_unambiguous:
                part_suffix = subsection_suffix
            elif subsection_suffix is None:
                part_suffix = f"(część {part_index}/{parts_total})"
            else:
                part_suffix = f"{subsection_suffix} (część {part_index}/{parts_total})"

            part_titles.append(part_suffix if title is None else f"{title} {part_suffix}")

        return part_titles

    @staticmethod
    def _create_subsection_suffix(part: list[LegalUnitElement]) -> str | None:
        subsections = [element.subsection for element in part if element.subsection is not None]
        if not subsections:
            return None

        if subsections[0] == subsections[-1]:
            return f"ust. {subsections[0]}"

        return f"ust. {subsections[0]}-{subsections[-1]}"


class RegulationType(StrEnum):
    ACT = "ACT"
    DECREE = "DECREE"
    STATUTE = "STATUTE"


class RegulationPreparationStatus(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    PREPARED = "PREPARED"
    FAILED = "FAILED"


@dataclass
class RegulationRegistrationData:
    presentation_name: str
    regulation_type: RegulationType | None = None
