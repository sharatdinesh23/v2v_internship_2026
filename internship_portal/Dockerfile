# Use official slim Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies including curl and git, then install Node.js (needed by Reflex)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Initialize Reflex app (runs reflex init to download/setup Node files under .web)
RUN reflex init

# Export the frontend as static files during build time
# Note: we need to ensure REFLEX_API_URL is available at build/export time so the static files point to the correct production backend url
ARG REFLEX_API_URL
ENV REFLEX_API_URL=${REFLEX_API_URL:-http://localhost:8010}
RUN reflex export --frontend-only --no-zip

# Expose the Reflex backend event server port
EXPOSE 8010

# Command to run only the backend server (the frontend static files will be served by Nginx)
CMD ["reflex", "run", "--backend-only", "--loglevel", "debug"]
