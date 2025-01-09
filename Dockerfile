# Use Python 3.11 slim as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-ben \
    poppler-utils \
    build-essential \
    python3-dev \
    libpq-dev \
    curl \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories with correct permissions
RUN mkdir -p \
    /app/storage/data \
    /app/storage/pdfs \
    /app/storage/temp \
    /app/storage/contributions \
    /app/logs \
    /.prisma \
    /root/.cache/prisma \
    && chmod -R 777 /.prisma \
    && chmod -R 777 /root/.cache/prisma

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application code
COPY . .

# Create script to generate .env file and handle Prisma
RUN echo '#!/bin/bash\n\
echo "Creating .env file..."\n\
env | grep -E "^(MONGODB_URL|REDIS_HOST|REDIS_PORT|REDIS_PASSWORD|ENVIRONMENT|DEBUG|GOOGLE_API_KEY|JWT_SECRET|SMTP_HOST|SMTP_PORT|SMTP_USER|SMTP_PASSWORD|API_URL|FRONTEND_URL|ENCRYPTION_KEY|CORS_ORIGINS|APP_NAME|HOST|PORT)" > .env\n\
echo ".env file created with $(wc -l < .env) variables"\n\
echo "Generating Prisma client..."\n\
prisma generate\n\
exec "$@"' > /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Set healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]