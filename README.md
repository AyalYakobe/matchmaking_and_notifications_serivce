# Matchmaking and Notification Service

This service performs donor–recipient matching by integrating with two external microservices (MS1 and MS2) and by storing resulting offers and notifications in a SQL database. It extends an OpenAPI-generated FastAPI backend with custom business logic and additional DB-backed endpoints.

---

## Overview

### Public Service Endpoints

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

1. Fetch organs from MS1  
2. Fetch needs from MS2  
3. Match based on organ type  
4. Delete matched organs and matched needs  
5. Store matches in SQL DB  
6. Generate an offer for each match  
7. Return structured results  

---

## Database-Backed Offers API

The OffersService provides:
- `GET /offers` — paginated list  
- `POST /offers` — create an offer  
- ETag support  
- Hypermedia (HATEOAS) links  
- `201 Created` responses with `Location` header  

---

## Internal Utilities

- `/db-test-c` — Cloud SQL connectivity test  
- MySQL creation + seed scripts  
- Idempotent SQL migration scripts  
- Pub/Sub publisher for Cloud Functions  

---

# ☁️ Cloud SQL Database Information  
*For class/demo use only (do NOT use these in production).*

Cloud SQL Instance ID: cloudsql2  
Public IP: 35.243.166.35  

Database: service_c_db  
Username: svc_c  
Password: SvcCpass1!  

Additional admin password (not used by service):  
Organdonation1!

---

# 🛠 Database Setup

### Create Tables
PYTHONPATH=src python3 src/openapi_server/db/create_tables.py

### Seed Dummy Data
PYTHONPATH=src python3 src/openapi_server/db/seed_dummy_data.py

### Test DB Connectivity
curl http://localhost:8000/db-test-c

---

# 🔧 Database Migration (migration1.sql)

Located at:

src/openapi_server/db/migrations/migration1.sql

This migration:

- Removes duplicate MATCHES records  
- Removes duplicate OFFERS records  
- Enforces UNIQUE constraints:
  - UNIQUE(donor_id, recipient_id)
  - UNIQUE(match_id)
- Creates performance indexes:
  - idx_matches_donor
  - idx_matches_recipient
  - idx_offers_match
- Fully idempotent  
- Compatible with Cloud SQL (MySQL 5.7/8.x)

### Run Migration

mysql -h 35.243.166.35 -u svc_c -p service_c_db < src/openapi_server/db/migrations/migration1.sql

Password: SvcCpass1!

### Verify Constraints

mysql -h 35.243.166.35 -u svc_c -p service_c_db -e "SHOW CREATE TABLE matches\G"
mysql -h 35.243.166.35 -u svc_c -p service_c_db -e "SHOW CREATE TABLE offers\G"

---

# ▶️ Running the FastAPI Service

### Install Dependencies
pip3 install -r requirements.txt

### Start the Service
PYTHONPATH=src uvicorn openapi_server.main:app --host 0.0.0.0 --port 8000

Docs: http://localhost:8000/docs

---

# 🧪 Running Tests

pip3 install pytest
PYTHONPATH=src pytest tests

---

# ☁️ Deployment — Google Cloud Run

gcloud run deploy matchmaking-service \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DB_HOST=35.243.166.35 \
  --set-env-vars DB_USER=svc_c \
  --set-env-vars DB_PASSWORD=SvcCpass1! \
  --set-env-vars DB_NAME=service_c_db \
  --set-env-vars DB_PORT=3306

