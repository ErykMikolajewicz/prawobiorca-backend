FROM python:3.14-slim-trixie

RUN pip install --no-cache uv==0.11.*

RUN useradd -r prawobiorca_app

RUN mkdir /files
RUN chown prawobiorca_app /files

WORKDIR /prawobiorca
RUN chown prawobiorca_app /prawobiorca


USER prawobiorca_app

COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock
RUN uv sync --compile-bytecode --no-cache --group local-storage

ENV PATH="/prawobiorca/.venv/bin:$PATH"

COPY app app
COPY main.py main.py

EXPOSE 8000

CMD ["granian", "--port", "8000", "--host", "0.0.0.0", "--interface", "asgi", "main:prawobiorca"]
