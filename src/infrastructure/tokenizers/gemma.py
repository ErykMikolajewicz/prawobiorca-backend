from pathlib import Path

from tokenizers import Tokenizer as HFTokenizer


class GemmaTokenizer:
    def __init__(self, tokenizer_path: str | Path | None = None):
        if tokenizer_path is None:
            tokenizer_path = Path(__file__).parent / "tokenizer.json"
        self._tokenizer = HFTokenizer.from_file(str(tokenizer_path))

    def count_tokens(self, text: str) -> int:
        encoding = self._tokenizer.encode(text)
        return len(encoding.tokens)
