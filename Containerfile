FROM python:3.13-slim-bookworm AS builder

COPY pyproject.toml pyproject.toml
RUN pip install --no-cache uv==0.7.*

COPY uv.lock uv.lock
RUN uv sync --compile-bytecode


FROM python:3.13-slim-bookworm
ARG IMAGE_VERSION

LABEL org.opencontainers.image.authors="Eryk Mikołajewicz <eryk.mikolajewicz@gmail.com>" \
      org.opencontainers.image.version=${IMAGE_VERSION} \
      org.opencontainers.image.description="Aplikacja webowa do wyszukiwania aktów prawnych prawobiorca." \
      org.opencontainers.image.source="https://github.com/ErykMikolajewicz/prawobiorca-backend" \
      maintainer="Eryk Mikołajewicz"

RUN useradd -r prawobiorca_app

USER prawobiorca_app

COPY --chown=prawobiorca_app:prawobiorca_app private.key certificate.crt /

ENV PATH="/.venv/bin:$PATH"

COPY --chown=prawobiorca_app:prawobiorca_app config /config
COPY --chown=prawobiorca_app:prawobiorca_app secrets /secrets
COPY --chown=prawobiorca_app:prawobiorca_app pyproject.toml pyproject.toml
COPY --chown=prawobiorca_app:prawobiorca_app .env .env

COPY --from=builder --chown=prawobiorca_app:prawobiorca_app  .venv /.venv

COPY --chown=prawobiorca_app:prawobiorca_app app /app

EXPOSE 8000

CMD ["granian", "--port", "8000", "--host", "0.0.0.0", "--interface", "asgi", "--ssl-certificate", "certificate.crt", \
 "--ssl-keyfile", "private.key", "app.main:app"]
