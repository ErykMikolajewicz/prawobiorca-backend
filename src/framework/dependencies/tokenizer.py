from src.app.ports.tokenizer import Tokenizer
from src.infrastructure.tokenizers.gemma import GemmaTokenizer


def get_tokenizer() -> Tokenizer:
    return GemmaTokenizer()
