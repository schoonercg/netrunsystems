FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_ENV=development
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_full.txt requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_full.txt

# Copy application code
COPY . .

# Create flask_session directory
RUN mkdir -p flask_session

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application with gunicorn (matching Azure deployment)
CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=1", "--timeout=600", "--access-logfile=-", "--error-logfile=-", "app:app"]