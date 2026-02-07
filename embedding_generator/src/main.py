from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request

from src.models import Embeddings, Texts
from src.onnx_encoding import OnnxEncoder


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


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
