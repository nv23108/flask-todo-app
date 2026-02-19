#!/bin/bash

# Read version from version.txt
VERSION=$(cat version.txt)
DOCKER_USERNAME="nv23108"
IMAGE_NAME="flask-todo-app"

echo "Building and pushing $IMAGE_NAME:$VERSION..."

# Build the image
docker build -t $IMAGE_NAME:$VERSION .

# Tag with username
docker tag $IMAGE_NAME:$VERSION $DOCKER_USERNAME/$IMAGE_NAME:$VERSION

# Also tag as latest
docker tag $IMAGE_NAME:$VERSION $DOCKER_USERNAME/$IMAGE_NAME:latest

# Push both tags
echo "Pushing to Docker Hub..."
docker push $DOCKER_USERNAME/$IMAGE_NAME:$VERSION
docker push $DOCKER_USERNAME/$IMAGE_NAME:latest

echo "✅ Successfully pushed $DOCKER_USERNAME/$IMAGE_NAME:$VERSION and :latest"
