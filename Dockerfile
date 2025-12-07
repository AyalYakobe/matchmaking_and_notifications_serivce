# ============================
# 1. Build / install dependencies
# ============================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies into /app/venv
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

RUN pip install --upgrade pip

COPY pyproject.toml .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# ============================
# 2. (Optional) Test runner
# ============================
FROM python:3.11-slim AS test_runner

WORKDIR /app
COPY --from=builder /app/venv /app/venv
COPY ./tests ./tests

ENV PATH="/app/venv/bin:$PATH"

RUN pip install pytest
RUN pytest tests


# ============================
# 3. Final service container
# ============================
FROM python:3.11-slim AS service

WORKDIR /app

# Bring in the virtualenv
COPY --from=builder /app/venv /app/venv
# Bring in the whole app source code
COPY . .

ENV PATH="/app/venv/bin:$PATH"

# Cloud Run listens on port 8080
ENV PORT=8080

# Start FastAPI with uvicorn
CMD ["uvicorn", "openapi_server.main:app", "--host", "0.0.0.0", "--port", "8080"]
