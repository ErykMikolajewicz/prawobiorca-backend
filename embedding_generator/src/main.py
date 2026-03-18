from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, Request, UploadFile
from src.models import Embeddings, Texts
from src.onnx_encoding import OnnxEncoder
from unstructured.partition.pdf import partition_pdf


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
async def parse_pdf(file: Annotated[UploadFile, File(...)]):
    elements = partition_pdf(file=file.file)

    return {"filename": file.filename, "elements": [element.to_dict() for element in elements]}


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
