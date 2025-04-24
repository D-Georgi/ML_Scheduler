#!/bin/bash

# Set image name for reference
export IMAGE_NAME=ml_scheduler_dolphins

# Build the Docker image
docker build -t $IMAGE_NAME .
