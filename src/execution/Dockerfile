# Use a base image with Python, JavaScript, and Node.js
FROM python:3.9-slim

# Install dependencies for Python and JavaScript execution
RUN apt-get update && apt-get install -y \
    curl \
    python3-pip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries (for code execution)
RUN pip install --no-cache-dir \
    pytest \
    flask \
    fastapi \
    transformers \
    torch

# Set up a directory for the app's code
WORKDIR /app

# Expose the port for API communication
EXPOSE 5000

# Command to keep the container running
CMD ["bash"]
