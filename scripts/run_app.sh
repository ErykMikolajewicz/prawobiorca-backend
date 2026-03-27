#!/bin/bash

set -e

run_container_if_not_running() {
  local name=$1
  shift
  local args="$@"

  if podman ps -a --format "{{.Names}}" | grep -q "^${name}$"; then

    if podman ps --format "{{.Names}}" | grep -q "^${name}$"; then
      echo "Container ${name} is already running - pass."
    else
      echo "Container ${name} already exist, but not running, launching."
      podman start "${name}"
    fi
  else
    echo "Create and launch container ${name}."
    podman run -d --name "${name}" ${args}
  fi
}


run_container_if_not_running postgres_db_prawobiorca \
  -e POSTGRES_PASSWORD=postgres \
  -p 127.0.0.1:5432:5432 \
  -v pg_data:/var/lib/postgresql \
  postgres:18


run_container_if_not_running qdrant_db_prawobiorca \
  -p 127.0.0.1:6333:6333 \
  -p 127.0.0.1:6334:6334 \
  -v qdrant_data:/qdrant/storage \
  qdrant/qdrant:latest


run_container_if_not_running text_transformator \
  -p 127.0.0.1:8080:8080 \
  text_transformator


granian \
  --port 8000 \
  --host 127.0.0.1 \
  --interface asgi \
  --ssl-certificate certificate.crt \
  --ssl-keyfile private.key \
  --reload main:prawobiorca
