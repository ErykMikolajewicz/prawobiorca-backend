from app.application.ports.tokenizer import Tokenizer
from app.infrastructure.tokenizers.gemma import GemmaTokenizer


def get_tokenizer() -> Tokenizer:
    return GemmaTokenizer()
