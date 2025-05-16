# Base Python image
FROM python:3.12-slim

# Set environment variables to suppress interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=xterm

# Update and install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-utils \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    curl \
    gnupg \
    iputils-ping \
    nano \
    dnsutils \
    procps \
    && curl -fsSL https://pgp.mongodb.com/server-6.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/mongodb-archive-keyring.gpg] https://repo.mongodb.org/apt/debian buster/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    mongodb-mongosh \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Suppress pip warnings about root user
ENV PIP_ROOT_USER_ACTION=ignore

# Copy project dependency files
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies
RUN python3 -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir --upgrade pip uv && \
    /app/.venv/bin/uv sync --python /app/.venv/bin/python && \
    ls -la /app/.venv/bin

# Copy the project files into the container
COPY . .

# Set the PYTHONPATH to the project root
ENV PYTHONPATH=/app

# Set environment variables for the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Ensure Python output is not buffered
ENV PYTHONUNBUFFERED=1
