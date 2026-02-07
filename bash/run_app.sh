#!/bin/bash

podman run -d \
  -e POSTGRES_PASSWORD=postgres \
  -p 127.0.0.1:5432:5432 \
  postgres:18

podman run -d \
  -p 127.0.0.1:6333:6333 \
  -p 127.0.0.1:6334:6334 \
  qdrant/qdrant:latest

podman run -d \
  -p 127.0.0.1:6379:6379 \
  redis:8 redis-server

podman run -d \
  -p 127.0.0.1:8080:8080 \
  embedding_generator redis-server


granian --port 8000 --host 127.0.0.1 --interface asgi --ssl-certificate certificate.crt --ssl-keyfile private.key \
--reload main:app

