from functools import partial
from pathlib import Path

from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer

model_root_dir = "/embedding_generator"

MODEL_ID = "onnx-community/embeddinggemma-300m-ONNX"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
tokenizer.save_pretrained(f"{model_root_dir}/onnx/tokenizer")

local_dir = Path(model_root_dir)
download_model_file = partial(hf_hub_download, MODEL_ID, subfolder="onnx", local_dir=local_dir)

model_path = download_model_file(filename=f"model.onnx")
download_model_file(filename=f"model.onnx_data")
