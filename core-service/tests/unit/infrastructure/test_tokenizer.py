from src.infrastructure.tokenizers.mmlw import MmlwTokenizer


def test_mmlw_tokenizer_counts_tokens():
    tokenizer = MmlwTokenizer()
    tokens_count = tokenizer.count_tokens("Art. 1. Ustawa określa zasady działania uczelni.")
    assert isinstance(tokens_count, int)
    assert tokens_count > 0
