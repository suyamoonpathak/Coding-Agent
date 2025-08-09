# Use an official Python image with GPU support (if available)
FROM python:3.9-slim

# Install necessary system libraries
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries (for LLM inference)
RUN pip install --no-cache-dir \
    transformers \
    torch \
    fastapi \
    uvicorn \
    numpy \
    faiss-cpu

# Set up a directory for the app's model code
WORKDIR /app

# Copy all files in the current src/models directory into the container /app directory
COPY . .
# Ensure Python sees this directory as a package root for absolute imports
ENV PYTHONPATH=/app

# Expose the port for FastAPI communication
EXPOSE 8000

# Command to run the FastAPI app (start model inference)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
