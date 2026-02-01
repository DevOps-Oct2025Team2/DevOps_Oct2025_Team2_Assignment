# Use an official slim Python base image
# - Smaller attack surface
# - Maintained by the Python team
FROM python:3.11-slim-bookworm

# Prevent interactive prompts during apt operations
# (important for non-interactive CI/CD environments)
ENV DEBIAN_FRONTEND=noninteractive

# Update OS packages and install only essential certificates
# - apt-get upgrade patches known OS vulnerabilities
# - ca-certificates required for HTTPS (pip, APIs, etc.)
# - --no-install-recommends keeps the image small
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security hardening
# Running applications as root is a common container vulnerability
RUN useradd -m appuser

# Set the working directory inside the container
# All subsequent commands run from /app
WORKDIR /app

# Copy dependency list first to leverage Docker layer caching
# Dependencies only reinstall if requirements.txt changes
COPY requirements.txt .

# Upgrade pip and install Python dependencies
# --no-cache-dir prevents pip cache from bloating the image
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application source code
COPY . .

# Create an uploads directory and give ownership to non-root user
# Required if the service writes files at runtime (e.g. uploaded files)
RUN mkdir -p /app/uploads && chown -R appuser:appuser /app/uploads

# Drop privileges and run as non-root user
USER appuser

# Document the port the Flask app listens on
# (informational but good practice for tooling and IaC)
EXPOSE 5002

# Start the Flask application
CMD ["python", "app.py"]
