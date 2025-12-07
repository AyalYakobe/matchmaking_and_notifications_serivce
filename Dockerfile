# ============================
# 1. Build / install dependencies
# ============================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install OS deps (important for MySQL + building wheels)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

RUN pip install --upgrade pip

# Copy requirement files
COPY pyproject.toml .
COPY requirements.txt .

# Install Python dependencies into venv
RUN pip install --no-cache-dir -r requirements.txt


# ============================
# 2. (Optional) Test runner (DISABLED)
# ============================
# If you want tests in Docker, uncomment & fix PYTHONPATH.
# FROM python:3.11-slim AS test_runner
# WORKDIR /app
# COPY --from=builder /app/venv /app/venv
# COPY . .
# ENV PATH="/app/venv/bin:$PATH"
# ENV PYTHONPATH="/app/src"
# RUN pip install pytest
# RUN pytest tests


# ============================
# 3. Final service container
# ============================
FROM python:3.11-slim AS service

WORKDIR /app

# Install OS deps needed at runtime (for MySQL)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/venv /app/venv

# Copy your whole app
COPY . .

ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Cloud Run listens on port 8080
ENV PORT=8080

# Start FastAPI with uvicorn
CMD ["uvicorn", "openapi_server.main:app", "--host", "0.0.0.0", "--port", "8080"]
