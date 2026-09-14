from typing import Protocol


class Tokenizer(Protocol):
    max_tokens: int
    title_tokens_overhead: int

    def count_tokens(self, text: str) -> int: ...
