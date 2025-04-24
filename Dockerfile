# Use an official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all source files
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

