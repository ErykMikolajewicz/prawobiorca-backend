from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from src.consts import MAX_TOKENS
from src.models import Embeddings, Texts
from src.onnx_encoding import OnnxEncoder


@asynccontextmanager
async def lifespan(application: FastAPI):
    encoder = OnnxEncoder()
    application.state.encoder = encoder
    yield


app = FastAPI(title="TextTransformator", lifespan=lifespan)


@app.post("/embed", response_model=Embeddings, responses={400: {"description": "Too long query."}})
def embed(texts: Texts, request: Request):
    texts = texts.model_dump()
    texts_encoder = request.app.state.encoder.encode
    try:
        embeddings = texts_encoder(texts)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "input_too_long",
                "message": "Input exceeds maximum token limit",
                "max_length": MAX_TOKENS,
            },
        )
    embeddings = Embeddings.model_validate(embeddings)
    return embeddings


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
