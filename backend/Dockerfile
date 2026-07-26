# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
ENV PYTHONDONTWRITEBYTECODE 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by pandas/numpy if any
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
# We use --no-cache-dir to keep the image small
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend source code and the ML models folder (since it relies on ../ml)
# Wait, the ML models are in /ml, not /backend. 
# We need to copy them in. But Docker build context is usually the directory of the Dockerfile.
# If this Dockerfile is run from the backend directory, it can't see ../ml.
# To fix this, we will run docker build from the root directory, or just copy the models we need.
# Assuming build context is `s:\EcoPackAI\EcoPackAI`
# Create a non-root user and switch to it for security
RUN adduser --disabled-password --gecos '' appuser

COPY --chown=appuser:appuser backend/ /app/
COPY --chown=appuser:appuser data/artifacts/ /data/artifacts/
COPY --chown=appuser:appuser data/processed/ /data/processed/
USER appuser

# Expose the port FastAPI runs on
EXPOSE 8000

# Run the web service on container startup using Uvicorn.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
