# Choose a basic lightwieght Python image
FROM python:3.11-slim

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required dependencies
RUN pip install .