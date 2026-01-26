podman run -d \
  -e POSTGRES_PASSWORD=postgres \
  -p 127.0.0.1:5432:5432 \
  postgres:latest

podman run -d \
  -p 127.0.0.1:6333:6333 \
  -p 127.0.0.1:6334:6334 \
  qdrant/qdrant:latest

podman run -d \
  -p 127.0.0.1:6379:6379 \
  redis:latest redis-server

