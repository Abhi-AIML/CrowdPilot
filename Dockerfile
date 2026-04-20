# Use a lightweight Python base image
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

# Create and set the working directory
WORKDIR /app

# Install system dependencies (needed for gevent/gunicorn if building from source)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-root user for security
RUN adduser --disabled-password --gevent "" crowduser
USER crowduser

# Expose the port
EXPOSE 8080

# Run the application with Gunicorn
# Using gevent worker class to support SSE streaming connections
CMD gunicorn --worker-class gevent --bind 0.0.0.0:$PORT --workers 1 --threads 8 "app:create_app()"
