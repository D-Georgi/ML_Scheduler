#!/bin/bash

# Set image name for reference
export IMAGE_NAME=ml_scheduler_dolphins

# Run the container
docker run -it -v "$PWD":/app $IMAGE_NAME /bin/bash
