# Use an official Python runtime as a parent image
FROM python:3.11.6-slim-bullseye AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory in the container to /app
WORKDIR /app

# Install system dependencies required for PostgreSQL and other tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11.6-slim-bullseye

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app \
    UVICORN_WORKERS=4 \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    RELOAD=false \
    BACKLOG=2048 \
    TIMEOUT_KEEP_ALIVE=5 \
    LIMIT_CONCURRENCY=1000 \
    LIMIT_MAX_REQUESTS=10000 \
    DATABASE_URL=postgresql://user:password@db:5432/dbname

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from previous stage
COPY --from=builder /root/.local /root/.local

# Set the working directory in the container to /app
WORKDIR /app

# Create logs directory
RUN mkdir -p /app/logs

# Copy the current directory contents into the container at /app
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health_check || exit 1

# Expose port
EXPOSE 8000

# Run the production server
CMD ["python", "run_production.py"]
