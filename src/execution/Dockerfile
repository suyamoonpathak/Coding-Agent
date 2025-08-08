# Use a base image with Python, JavaScript, and Node.js. This one is for Python, if we need more languages, we need more containers like this.
# Use a base image with Python, JavaScript, and Node.js
FROM python:3.9-slim

# Install dependencies for Python and JavaScript execution
RUN apt-get update && apt-get install -y \
    curl \
    python3-pip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Create a new non-root user for running code securely
RUN useradd -ms /bin/bash coder

# Create docker group with host GID and add coder user to it
RUN groupadd -g 1001 docker && usermod -aG docker coder

# Install Python libraries (for code execution)
RUN pip install --no-cache-dir \
    pytest \
    flask \
    fastapi \
    # transformers \
    # torch \
    uvicorn\
    docker

# Set up a directory for the app's code
WORKDIR /app

COPY . .


# Change to the non-root user
USER coder

# Expose the port for API communication
EXPOSE 5000

# Command to run FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]

