from unittest.mock import MagicMock

from app.domain.value_objects.regulations import RegulationAct, RegulationElement, UsefulLabels


def test_regulation_act_assigns_chunk_order():
    elements = [
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="Header 1"),
        RegulationElement(label=UsefulLabels.TEXT, text="Content 1"),
        RegulationElement(label=UsefulLabels.TEXT, text="Content 1.1"),
        RegulationElement(label=UsefulLabels.SECTION_HEADER, text="Header 2"),
        RegulationElement(label=UsefulLabels.TEXT, text="Content 2"),
        RegulationElement(label=UsefulLabels.TEXT, text="Content 2.1"),
    ]

    mock_tokenizer = MagicMock()
    mock_tokenizer.count_tokens.return_value = 10

    act = RegulationAct(elements, mock_tokenizer)
    collection = act.get_documents_to_embed()
    documents = list(collection)

    assert len(documents) == 2

    doc_1 = next(d for d in documents if "Content 1" in d.text)
    doc_2 = next(d for d in documents if "Content 2" in d.text)

    assert doc_1.chunk_order == 0
    assert doc_2.chunk_order == 1
