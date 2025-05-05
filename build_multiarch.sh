#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Prompt user to enter Docker Hub username
read -p "Enter Docker Hub username: " DOCKER_USERNAME
if [ -z "$DOCKER_USERNAME" ]; then
    echo "No username provided, using default: arnozeng"
    DOCKER_USERNAME="arnozeng"
fi

# Login to Docker Hub
echo "Logging in to Docker Hub..."
docker login -u ${DOCKER_USERNAME}

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
BACKEND_IMAGE=${DOCKER_USERNAME}/scc-backend
FRONTEND_IMAGE=${DOCKER_USERNAME}/scc-frontend
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