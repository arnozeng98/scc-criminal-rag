#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Set up Docker Buildx builder if not exists
if ! docker buildx inspect multiarch-builder &>/dev/null; then
    echo "Creating new Docker Buildx builder"
    docker buildx create --name multiarch-builder --use
else
    echo "Using existing Docker Buildx builder"
    docker buildx use multiarch-builder
fi

# Start the builder
docker buildx inspect --bootstrap

# Variables
BACKEND_IMAGE=arnozeng/scc-backend
FRONTEND_IMAGE=arnozeng/scc-frontend
TAG=latest

# Build and push backend multi-architecture image
echo "Building and pushing multi-architecture backend image..."
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag ${BACKEND_IMAGE}:${TAG} \
    --file docker/backend.Dockerfile \
    --push \
    .

# Build and push frontend multi-architecture image
echo "Building and pushing multi-architecture frontend image..."
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag ${FRONTEND_IMAGE}:${TAG} \
    --file docker/frontend.Dockerfile \
    --push \
    .

echo "Multi-architecture images built and pushed successfully!"
echo "Backend image: ${BACKEND_IMAGE}:${TAG}"
echo "Frontend image: ${FRONTEND_IMAGE}:${TAG}" 