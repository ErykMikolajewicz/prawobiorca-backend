from src.infrastructure.tokenizers.gemma import GemmaTokenizer


def test_gemma_tokenizer_counts_tokens():
    tokenizer = GemmaTokenizer()
    tokens_count = tokenizer.count_tokens("Art. 1. Ustawa określa zasady działania uczelni.")
    assert isinstance(tokens_count, int)
    assert tokens_count > 0
