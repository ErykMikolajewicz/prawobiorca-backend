#!/bin/bash

IMAGE_VERSION="2"
IMAGE_NAME="prawobiorca-backend-dev"

podman build \
  --file Containerfile \
  --build-arg IMAGE_VERSION="$IMAGE_VERSION" \
  --tag "$IMAGE_NAME:$IMAGE_VERSION" .

echo "Image builded: $IMAGE_NAME:$IMAGE_VERSION"
