import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from docling.document_converter import DocumentConverter
from fastapi import FastAPI, File, Request, UploadFile
from src.models import Embeddings, Texts
from src.onnx_encoding import OnnxEncoder
from src.services import add_tokens_info

converter = DocumentConverter()


@asynccontextmanager
async def lifespan(_: FastAPI):
    encoder = OnnxEncoder()
    app.state.encoder = encoder
    yield


app = FastAPI(title="EmbeddingGemma Service", lifespan=lifespan)


@app.post("/api/embed", response_model=Embeddings)
def embed(texts: Texts, request: Request):
    texts = texts.model_dump()
    texts_encoder = request.app.state.encoder.encode
    embeddings = texts_encoder(texts)
    embeddings = Embeddings.model_validate(embeddings)
    return embeddings


@app.post("/api/parse-pdf")
def parse_pdf(file: Annotated[UploadFile, File(...)], request: Request):
    with tempfile.NamedTemporaryFile("wb") as temp_file:
        file_content = file.file.read()
        temp_file.write(file_content)
        file_path = temp_file.name
        file_path = Path(file_path)

        result = converter.convert(file_path)

    tokens_counter = request.app.state.count_tokens
    texts = result.document.texts
    add_tokens_info(texts, tokens_counter)

    return


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
