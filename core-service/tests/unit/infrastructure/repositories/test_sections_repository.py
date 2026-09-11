from unittest.mock import AsyncMock
from uuid import uuid4

from src.domain.value_objects.sections import RegulationSection, SectionChunk, SectionsCollection
from src.infrastructure.relational_db.repositories.sections import RegulationsSectionsRepository


def create_sections_collection() -> SectionsCollection:
    return SectionsCollection(
        [
            RegulationSection(
                header="Art. 1",
                text="Content 1 Content 2",
                chunks=[
                    SectionChunk(text="Content 1", embed_title="Art. 1 ust. 1", chunk_index=0, vector=[0.1]),
                    SectionChunk(text="Content 2", embed_title="Art. 1 ust. 2", chunk_index=1, vector=[0.2]),
                ],
                section_order=0,
            ),
            RegulationSection(
                header="Art. 2",
                text="Content 3",
                chunks=[SectionChunk(text="Content 3", embed_title="Art. 2", chunk_index=0, vector=[0.3])],
                section_order=1,
            ),
        ]
    )


async def test_add_sections_saves_sections_order():
    session = AsyncMock()

    await RegulationsSectionsRepository.add_sections(session, uuid4(), uuid4(), create_sections_collection())

    sections_stmt = session.execute.await_args_list[0].args[0]
    inserted_values = sections_stmt.compile().params

    sections_orders = sorted(value for key, value in inserted_values.items() if key.startswith("section_order"))

    assert sections_orders == [0, 1]


async def test_add_sections_saves_chunks_with_their_section():
    session = AsyncMock()
    sections = create_sections_collection()

    await RegulationsSectionsRepository.add_sections(session, uuid4(), uuid4(), sections)

    chunks_stmt = session.execute.await_args_list[1].args[0]
    inserted_values = chunks_stmt.compile().params

    section_ids = [value for key, value in inserted_values.items() if key.startswith("section_id")]
    chunk_indexes = [value for key, value in inserted_values.items() if key.startswith("chunk_index")]

    first_section, second_section = sections
    assert section_ids == [first_section.id, first_section.id, second_section.id]
    assert chunk_indexes == [0, 1, 0]
