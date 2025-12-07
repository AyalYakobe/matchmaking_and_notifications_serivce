###############################################
# 1. Builder stage - install dependencies
###############################################
FROM python:3.11-slim AS builder

WORKDIR /app

# Install OS dependencies needed for MySQL + building wheels
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Upgrade pip
RUN pip install --upgrade pip

# Copy dependency files
COPY pyproject.toml .
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


###############################################
# 2. Final runtime image
###############################################
FROM python:3.11-slim AS service

WORKDIR /app

# Install OS runtime dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /app/venv /app/venv

# Copy full project into image
COPY . .

# Activate venv
ENV PATH="/app/venv/bin:$PATH"

# Point Python to src folder (so openapi_server is discoverable)
ENV PYTHONPATH="/app/src"

# Cloud Run listens on port 8080
ENV PORT=8080

# Launch FastAPI via uvicorn
CMD ["uvicorn", "src.openapi_server.main:app", "--host", "0.0.0.0", "--port", "8080"]
