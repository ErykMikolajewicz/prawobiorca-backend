from typing import Protocol


class Tokenizer(Protocol):
    def count_tokens(self, text: str) -> int: ...
