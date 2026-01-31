# Use a slim, officially maintained Python base image
FROM python:3.11-slim-bookworm

# Disable interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update and patch OS packages to fix security vulnerabilities
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to improve container security
RUN useradd -m appuser

# Set the working directory inside the container
WORKDIR /app

# Copy dependency list to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies without caching
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --upgrade --force-reinstall \
       wheel>=0.46.2 \
       jaraco.context>=6.1.0 \
    && pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the application source code into the container
COPY . .

# Run the application as a non-root user
USER appuser

# Start the Python application when the container launches
CMD ["python", "app.py"]