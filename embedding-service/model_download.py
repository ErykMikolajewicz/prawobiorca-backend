import tempfile
from functools import partial
from pathlib import Path

from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer

model_root_dir = "/embedding-service"

MODEL_ID = "onnx-community/embeddinggemma-300m-ONNX"

with tempfile.TemporaryDirectory() as tmpdir:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, cache_dir=tmpdir, force_download=True)
    tokenizer.save_pretrained(f"{model_root_dir}/onnx/tokenizer")

    local_dir = Path(model_root_dir)
    download_model_file = partial(hf_hub_download, MODEL_ID, subfolder="onnx", local_dir=local_dir, cache_dir=tmpdir)

    model_path = download_model_file(filename="model.onnx")
    download_model_file(filename="model.onnx_data")
