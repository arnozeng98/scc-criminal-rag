FROM --platform=${BUILDPLATFORM:-linux/amd64} python:3.9-slim AS builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM --platform=${TARGETPLATFORM:-linux/amd64} python:3.9-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Ensure uvicorn is executable
RUN chmod +x /usr/local/bin/uvicorn

# Copy backend code
COPY backend/ ./backend/

# Copy data directory into the image
COPY data/ ./data/

# Environment variables
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run API server
CMD ["uvicorn", "backend.src.api.app:app", "--host", "0.0.0.0", "--port", "8000"] 