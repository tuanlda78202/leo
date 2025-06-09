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
    procps && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv globally
RUN pip install --no-cache-dir uv

# Set the working directory inside the container
WORKDIR /app

# Copy ALL project files first (needed for editable install)
COPY . .

# Install dependencies and the project globally using uv
RUN uv pip install --system -e .

# Set the PYTHONPATH to the project root
ENV PYTHONPATH=/app

# Ensure Python output is not buffered
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 7820

# Use the global uvicorn installation
ENTRYPOINT ["uvicorn", "tools.api:app", "--host", "0.0.0.0", "--port", "7820", "--reload"]
