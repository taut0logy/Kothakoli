# Use Python 3.11 slim as base image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-ben \
    poppler-utils \
    build-essential \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p storage/data storage/pdfs storage/temp storage/contributions storage/temp logs

# Create script to generate .env file
# RUN echo '#!/bin/bash\n\
# echo "Creating .env file..."\n\
# env | grep -E "^(MONGODB_URL|REDIS_URL|ENVIRONMENT|DEBUG|GOOGLE_API_KEY|JWT_SECRET|SMTP_|API_|FRONTEND_URL|ENCRYPTION_KEY|CORS_|APP_)" > .env\n\
# echo ".env file created with $(wc -l < .env) variables"\n\
# exec "$@"' > /app/docker-entrypoint.sh && \
#     chmod +x /app/docker-entrypoint.sh

# Set permissions
RUN chmod -R 755 storage logs

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Set healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1


# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"] 