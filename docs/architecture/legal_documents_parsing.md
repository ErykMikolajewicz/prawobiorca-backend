# Legal Documents Parsing

This page explains how a PDF regulation becomes a set of sections with embedded chunks, and why the
chunking logic does not rely on the layout labels produced by the extraction service.

---

## Pipeline Overview

```text
PDF ──► extraction-service (Docling) ──► [{label, text}, ...] ──► LegalStructureParser ──► [LegalUnit, ...]
                                                                                              │
                                                                           RegulationAct chunking
                                                                                              ▼
                                                                     [RegulationSection, ...] ──► chunk embeddings
```

`extraction-service` stays deliberately dumb: it runs layout analysis and returns a flat list of text
elements with their layout labels (`section_header`, `list_item`, `text`, `page_header`, ...). All knowledge
about legal structure lives in the `core-service` domain layer.

---

## Why Layout Labels Are Not Enough

The obvious approach — group elements by `section_header` — works only for documents where every editorial
unit opens its own visual heading, such as the PWr study regulations, where `§ 5 .` is a separate centered line.

It breaks on acts published in the `Dziennik Ustaw` format, where an article opens the **same paragraph** as
its first subsection:

```json
{"label": "text", "text": "Art. 107. 1. Student jest obowiązany postępować zgodnie z treścią ślubowania..."}
{"label": "text", "text": "Art. 108. 1. Studenta skreśla się z listy studentów w przypadku:"}
```

Docling labels those blocks as `text`, because visually they are ordinary paragraphs. The only `section_header`
elements in the whole act are the chapter headings, so grouping by label produces one giant section per chapter,
chunk boundaries fall in the middle of articles, and the stored header is a useless `"Rozdział 5Pracownicy uczelni"`.

Layout signals do not help either:

- `TextItem.formatting` is not populated by the PDF pipeline used by the service, so bold headings cannot be detected.
- `TextItem.prov[0].bbox.l` is the minimum over all lines of a block, so paragraph indentation is only visible for
  single-line blocks — `Art. 107.` reports `l=72.0`, while the two-line `Art. 109.` already reports `l=51.0`.

The structure is therefore recovered from the **text itself**, using the numbering scheme mandated by
*Zasady techniki prawodawczej*, which every Polish legal act follows.

---

## Editorial Units

| Unit | Notation | Recognised as |
|------|----------|---------------|
| dział / rozdział / oddział / część / księga / tytuł | `Rozdział 4`, `DZIAŁ VII` | breadcrumb segment (`LegalUnit.path`) |
| artykuł | `Art. 107.` | retrieval unit (`UnitType.ARTICLE`) |
| paragraf | `§ 6 .` | retrieval unit (`UnitType.PARAGRAPH`) or content, see below |
| ustęp | `1.` | element boundary, kept in `LegalUnitElement.subsection` |
| punkt | `1)` | element boundary, inherits the subsection above it |
| litera | `a)` | element boundary, inherits the subsection above it |

Two rules deserve attention:

- **Articles win over paragraphs.** If a document contains at least one `Art.`, then `§` is treated as content,
  because in Polish codes the paragraph is a *subunit* of an article (`Art. 5. § 2.`). Only documents without
  articles — university regulations, internal rules — use `§` as their top-level unit.
- **References are not units.** The patterns are anchored at the start of an element and require the capital
  `Art.`, so an in-text reference such as `"o których mowa w art. 86 ust. 1 pkt 1-4"` never starts a new unit.

A unit marker is matched differently depending on the element: a content element must **open** with it, while
a `section_header` may carry it anywhere, because real documents put it in every possible position — `§ 5 . Title`,
`Title § 2`, or a bare `§ 1` on the line below its title. In the last case the preceding heading becomes the title
of the unit instead of a breadcrumb segment.

Divisions are recognised only on elements labelled `section_header` — in Polish acts they are always centered
headings, and Docling detects those reliably. A `section_header` that carries no division keyword becomes
a breadcrumb segment of the lowest rank, which keeps unstructured documents working as before.

---

## Sections and Chunks

`RegulationAct` turns every unit into one `RegulationSection` — the unit of **presentation** — holding
1..N `SectionChunk` objects, the units of **retrieval**. The user always sees a whole editorial unit;
chunking exists only so that a long article still embeds well.

- Every unit with content becomes exactly **one** section, carrying the full unit text and the full
  breadcrumb as its `header`. Short articles are never merged with their neighbours.
- The section is split into chunks of at most `APP_CHUNK_MAX_TOKENS` tokens (200 by default). A boundary
  may only fall **between** elements (subsections, points).
- An element longer than the budget is split on sentence boundaries, and — as a last resort — on token counts.
  Nothing raises: a single oversized paragraph must not fail the whole regulation.
- Each chunk carries an `embed_title` used only for the embedding prefix: the breadcrumb, trimmed from the
  top when it grows too long, plus a subsection range suffix (`ust. 6-8`), extended with `(część 2/4)` when
  the ranges alone would not be unique. The suffixes never reach the user — `section.header` has none.

Every section also stores its structural metadata (`unit_type`, `unit_number`, `unit_path`), which is what
search results use for citations such as *"Art. 108, Prawo o szkolnictwie wyższym"*.

---

## Scoring

A query hits chunks, but the score is reported per section. Chunks of one section are ranked by cosine
similarity and the two best ones are combined:

```text
score = 0.8 * best_chunk + 0.2 * second_best_chunk       (section with 2+ chunks)
score = 1.0 * best_chunk                                 (section with exactly 1 chunk)
```

The weights come from `APP_PRIMARY_CHUNK_SCORE_WEIGHT` (the secondary weight is its complement), so they
always sum to 1 and the score stays on the cosine scale — it is shown to the user as-is. `threshold` and
`limit` of a search apply to this combined section score. The whole computation is one SQL statement in
`RegulationsSectionsRepository.search`.

---

## Extending the Parser

New patterns belong in `../../core-service/src/domain/services/legal_structure_parser.py`, as module-level
constants next to the existing ones. When adding a unit type, remember to:

1. add its pattern and, for divisions, its rank in `DIVISION_RANKS`,
2. decide how it interacts with the article-versus-paragraph rule in `_detect_unit_type`,
3. cover it with a regression test in `../../core-service/tests/unit/domain/services/test_legal_structure_parser.py`,
   preferably against a real extraction fixture from `../../core-service/tests/data`.
