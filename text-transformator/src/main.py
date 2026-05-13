import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from fastapi import FastAPI, File, HTTPException, Request, UploadFile, status
from src.consts import MAX_TOKENS
from src.models import Embeddings, Texts
from src.onnx_encoding import OnnxEncoder
from src.services import add_tokens_info


@asynccontextmanager
async def lifespan(application: FastAPI):
    accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CPU)

    pipeline_options = PdfPipelineOptions()
    pipeline_options.accelerator_options = accelerator_options

    application.state.converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )
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


@app.post("/parse-regulation")
def parse_pdf(file: Annotated[UploadFile, File(...)], request: Request):
    converter = request.app.state.converter
    with tempfile.NamedTemporaryFile("wb", suffix=".pdf", delete=False) as temp_file:
        file_content = file.file.read()
        temp_file.write(file_content)
        file_path = temp_file.name
        file_path = Path(file_path)

    try:
        result = converter.convert(file_path)
    finally:
        file_path.unlink()

    tokens_counter = request.app.state.encoder.count_tokens
    texts = result.document.texts
    document_with_tokens = add_tokens_info(texts, tokens_counter)

    return document_with_tokens


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
