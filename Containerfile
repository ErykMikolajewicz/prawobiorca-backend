FROM python:3.13-slim-bookworm AS builder

RUN pip install --no-cache uv==0.9.*

RUN useradd -r prawobiorca_app

WORKDIR /prawobiorca

COPY --chown=prawobiorca_app:prawobiorca_app pyproject.toml pyproject.toml
COPY uv.lock uv.lock
RUN uv sync --compile-bytecode

USER prawobiorca_app

COPY --chown=prawobiorca_app:prawobiorca_app private.key certificate.crt /prawobiorca/

ENV PATH="/prawobiorca/.venv/bin:$PATH"

COPY --chown=prawobiorca_app:prawobiorca_app .env .env

COPY --chown=prawobiorca_app:prawobiorca_app app app
COPY --chown=prawobiorca_app:prawobiorca_app main.py main.py

EXPOSE 8000

CMD ["granian", "--port", "8000", "--host", "0.0.0.0", "--interface", "asgi", "--ssl-certificate", "certificate.crt", \
 "--ssl-keyfile", "private.key", "main:app"]
