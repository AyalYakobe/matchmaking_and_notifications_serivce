# Matchmaking and Notification Service

This service performs donor–recipient matching by integrating with two external microservices (MS1 and MS2) and by storing resulting offers and notifications in a SQL database. It extends an OpenAPI-generated FastAPI backend with custom business logic and additional DB-backed endpoints.

---

## Overview

## Public Service Endpoints

- **Base API URL:** http://34.138.171.147:8000  
- **Swagger UI:** http://34.138.171.147:8000/docs  
- **ReDoc:** http://34.138.171.147:8000/redoc

### Passthrough API to MS1 (Donor Registry)
Read-only passthrough endpoints for:
- Donors
- Organs
- Consents

### Passthrough API to MS2 (Recipient Registry)
Read-only passthrough endpoints for:
- Recipients
- Needs
- Hospitals

---

## Matchmaking Logic

The service orchestrates donor–recipient matching:
1. Fetches organs from MS1  
2. Fetches needs from MS2  
3. Matches items based on organ type  
4. Deletes matched organs and needs  
5. Returns structured match results  

---

## Database-Backed Offers API

The OffersService provides:
- `GET /offers`
- `POST /offers`
- Pagination support
- ETag support
- `201 Created` with `Location` header
- Linked response format

---

## Internal Utilities

- `/db-test-c` — verifies Cloud SQL connectivity  
- Create/seed scripts for local or Cloud SQL initialization  

---

## Requirements

- Python 3.11+
- MySQL / Cloud SQL
- Access to MS1 + MS2 endpoints

---

## Installation & Running

### Install dependencies
```bash
pip3 install -r requirements.txt
```

### Run the FastAPI service
```bash
PYTHONPATH=src uvicorn openapi_server.main:app --host 0.0.0.0 --port 8080
```

OpenAPI docs: http://localhost:8080/docs

---

## Database Setup

### Create tables
```bash
PYTHONPATH=src python3 src/openapi_server/db/create_tables.py
```

### Insert dummy data
```bash
PYTHONPATH=src python3 src/openapi_server/db/seed_dummy_data.py
```

### Test DB connectivity
```bash
curl http://localhost:8080/db-test-c
```

---

## Running with Docker
```bash
docker compose up --build
```

---

## Running Tests
```bash
pip3 install pytest
PYTHONPATH=src pytest tests
```

---

## Deployment (Google Cloud Run)
```bash
gcloud run deploy matchmaking-service \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DB_HOST=... \
  --set-env-vars DB_USER=... \
  --set-env-vars DB_PASSWORD=... \
  --set-env-vars DB_NAME=... \
  --set-env-vars DB_PORT=3306
```

### Ensure:
- Cloud SQL instance allows Cloud Run connections  
- Public IP or VPC connector is configured  
- Service account has SQL Client permission  

---

## Notes

This project extends an OpenAPI-generated FastAPI server with custom capabilities:

### Features
- Matchmaking orchestrator  
- DB-backed Offers endpoints  
- Passthrough API to MS1 and MS2  
- Composite-service integration  

### Future Extensions
- Notification dispatch pipeline  
- Async job orchestration  
- Enhanced compatibility scoring  


http://34.138.171.147:8000/docs
http://34.138.171.147:8000
