from collections.abc import Iterable

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer


class OnnxEncoder:
    def __init__(self):
        self.__initialize_session()

    def __initialize_session(self):
        model_path = "/embedding_generator/onnx/model.onnx"
        self.__session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])

        self.__tokenizer = Tokenizer.from_file("/embedding_generator/onnx/tokenizer/tokenizer.json")
        self.__tokenizer.enable_padding(length=None, pad_id=0)

    def encode(self, texts: Iterable[str]) -> list[list[float]]:
        encodings = self.__tokenizer.encode_batch(texts)
        input_ids = np.array([e.ids for e in encodings], dtype=np.int64)
        attention_mask = np.array([e.attention_mask for e in encodings], dtype=np.int64)

        onnx_inputs = {"input_ids": input_ids, "attention_mask": attention_mask}

        _, embeddings = self.__session.run(None, onnx_inputs)

        embeddings = embeddings.tolist()

        return embeddings

    def count_tokens(self, text: str) -> int:
        encoding = self.__tokenizer.encode(text)
        tokens_number = encoding.n_sequences
        return tokens_number
