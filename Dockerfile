# OpenEncroachment Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/src
ENV OPENAI_API_KEY=""

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && \
    uv sync --frozen --no-install-project

# Copy source code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p artifacts/models artifacts/predictions outbox logs data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uv", "run", "uvicorn", "open_encroachment.api:app", "--host", "0.0.0.0", "--port", "8000"]
