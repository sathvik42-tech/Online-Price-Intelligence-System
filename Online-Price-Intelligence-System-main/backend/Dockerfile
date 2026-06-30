# Dockerfile for Python Backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create upload directory
RUN mkdir -p static/uploads

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "uvicorn", "app.main_optimized:app", "--host", "0.0.0.0", "--port", "8000"]
