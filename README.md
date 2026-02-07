# 📦 Project Local Setup & Architecture Guide

This repository documents how the team runs the project **locally** using a **standardised setup**, ensuring that developers, lecturers, testers, and CI runners can all execute the system **consistently and reliably**. 

---

## 🔍 High-Level Overview

This project is built using a **multi-service backend architecture**.

* The system consists of multiple **Flask backend services**
  (e.g. `auth-service`, `file-service`)
* Each service:

  * Has its **own PostgreSQL database**
  * Is started using **Docker Compose**
* PostgreSQL runs **inside Docker containers**

  * No manual database installation required
* **Database schema is shared via migrations**

  * Migration files are committed to Git
  * Actual data is **never shared**
* Every developer has:

  * Their own local data
  * The same database structure

---

## 🧠 Key Concepts Explained

### 1️⃣ Docker-Managed Databases

* Docker Compose starts all databases (e.g. `auth-db`, `file-db`)
* Everyone runs:

  * The same database engine
  * The same version
* Data is stored in **Docker volumes**

  * Containers can restart without data loss
  * Data is deleted **only** if volumes are explicitly removed

---

### 2️⃣ Service Independence

Each backend service is fully isolated:

* Independent Flask application
* Separate database connection
* Own database tables
* Own `migrations/` folder

This design:

* Prevents cross-service interference
* Improves scalability
* Simplifies testing and ownership

---

### 3️⃣ Database Migrations (No Manual Table Creation)

* Tables are defined using Python models (`models.py`)
* `Flask-Migrate` generates migration scripts
* Migration files are committed to Git
* Any developer or CI runner can recreate the schema by running migrations

This guarantees:

* Identical database structures for everyone
* No shared data
* Repeatable setup for grading and CI

---

### 4️⃣ Clear Ownership Responsibilities

* `auth-service` developer owns:

  * Auth tables
  * Auth migrations
* `file-service` developer owns:

  * File tables
  * File migrations
* Team members:

  * Pull migrations from Git
  * Apply them locally

This avoids:

* Conflicts
* Accidental schema changes
* Responsibility ambiguity

---

### 5️⃣ Sample Users for Local Testing

* A script is provided to insert sample users into the auth database
* Passwords are securely hashed
* The script is **idempotent**

  * Safe to re-run
  * No duplicate users

This supports smooth local development and testing.

---

## 📁 File Service — User Dashboard (MVP)

### Overview

The **User Dashboard** is part of the File Service backend.

It allows an authenticated user to retrieve **only their own uploaded files**.

* Ownership checks are enforced **server-side**
* Prevents data leakage between users
* Built using **Test-Driven Development (TDD)**
* Fully verified via automated backend tests

---

### 📡 Endpoint

```
GET /dashboard
```

---

### 🎯 Purpose

* Display files uploaded by the authenticated user
* Prevent access to other users’ files
* Return an empty list when no files exist

---

## 🔐 Security & Access Rules (Acceptance Criteria)

### AC-DASH-01 — Authorised Access

* User must be authenticated
* Valid request returns **HTTP 200**

### AC-DASH-02 — Unauthorised Access Prevention

* If user is not authenticated:

  * Access is denied
  * **HTTP 401 Unauthorized** is returned

### AC-DASH-03 — User Data Isolation *(Security-Critical)*

* Only files owned by the authenticated user are returned
* Ownership enforced server-side
* Client-side manipulation cannot expose other users’ data
* Test failure **fails the CI pipeline**

### AC-DASH-04 — Empty State Handling

* If user has no uploaded files:

  * An empty list is returned
  * No errors occur

---

## 🔑 Authentication (Local Development)

For local testing, authentication is simulated using an HTTP header:

```
X-User-Id: <user_id>
```

Example:

```
X-User-Id: 1
```

This allows dashboard logic and security rules to be tested **independently** of the auth service.

---

## 📤 Dashboard Response Format

### Example Response

```json
{
  "files": [
    {
      "id": 1,
      "filename": "example.txt",
      "storage_path": "/files/example.txt",
      "content_type": "text/plain",
      "size_bytes": 1234,
      "created_at": "2026-01-17T12:00:00Z"
    }
  ]
}
```

### Empty State

```json
{
  "files": []
}
```

---

## 🧪 Automated Testing — Ownership Isolation

### What the Test Verifies

* Multiple users exist in the database
* Each user can own files
* When the dashboard is queried for **User A**:

  * Only User A’s files are returned
  * Files owned by others are never exposed

This directly validates **AC-DASH-03 (Security-Critical)**.

---

## ▶️ Running Tests Locally (File Service)

### Important Note

Unit tests are **fully isolated** and do **not** require:

* Docker
* PostgreSQL

Test environments:

* `auth-service`: mocked dependencies
* `file-service`: in-memory database

This ensures:

* Fast execution
* Deterministic results
* CI-safe testing

### Run Tests

```bash
cd file_service
pytest
```

### Expected Output

```
1 passed
```

Failure indicates a security or ownership violation and blocks the pipeline.

---

## 🔐 Auth Service — Unit Testing

### Overview

Auth-service tests are **true unit tests** and do not rely on:

* Real databases
* Docker containers
* JWT key files on disk

All cryptographic dependencies are injected or mocked.

---

### ▶️ Running Auth-Service Tests

```bash
cd auth-service
pip install -r requirements.txt
pytest -v
```

---

### Environment Configuration

* JWT signing and verification keys are provided via environment variables
* No PEM files are read from disk

This allows tests to run safely in:

* Local development
* CI pipelines
* Isolated test environments

---

### Expected Output (Excerpt)

```
==================== all tests passed ====================
```

---

## 🧩 Design Notes

- Tests are true unit tests
- No filesystem access is required
- No secrets are committed to Git
- No production credentials are used
- Test failures will fail the CI pipeline

# 📂 File Service – User Dashboard & File Upload

This service provides backend APIs for:
- Viewing a user’s uploaded files (`GET /dashboard`)
- Uploading a new file (`POST /dashboard/upload`)

The service enforces **user data isolation**, **upload validation**, and **server-side ownership checks**.

---

## 🚀 How to Run (Local Development)

### 1. Start required services
From the project root:

```bash
docker-compose up -d
This starts:

file-db (PostgreSQL on port 5434)

auth-db (PostgreSQL on port 5433)

2. Install Python dependencies
cd file_service
pip install -r requirements.txt
⚠️ Ensure flask-cors is installed (already included in requirements.txt).

3. Run database migrations
python -m flask db upgrade
4. Start the File Service
python app.py
The service runs on:

http://localhost:5000
🔍 Health Check
Open in browser:

http://localhost:5000/health
Expected response:

{ "status": "ok" }
📄 API: View Dashboard Files
Endpoint
GET /dashboard
Required Header
X-User-Id: <number>
Example:

X-User-Id: 1
How to Test (curl)
curl -H "X-User-Id: 1" http://localhost:5000/dashboard
Expected Results
✅ Authenticated user

{
  "files": []
}
(Empty list means no uploaded files)

❌ Unauthenticated / invalid user

HTTP 401 Unauthorized

📤 API: Upload File
Endpoint
POST /dashboard/upload
Required Header
X-User-Id: <number>
Request Type
multipart/form-data
Field Name
file
How to Test (UI – Recommended)
Start UI Gateway:

cd ui-gateway
python app.py
Open browser:

http://localhost:3000
Login (development mode)

Upload a file from the dashboard page

Upload Rules
Only allowed file types are accepted

File size must be within configured limits

Validation is enforced server-side

Expected Results
✅ Valid file

HTTP 201 Created

File is stored

File appears in dashboard

❌ Invalid file (e.g. mp4 / too large)

HTTP 400 Bad Request

{
  "error": "The uploaded file does not meet the upload requirements."
}
No file is stored

🔐 Security Guarantees
Users can only access their own files

Ownership checks are enforced server-side

Client-side manipulation cannot expose other users’ data

🧪 Running Tests
pytest
Tests are fully isolated

Uses in-memory SQLite

No Docker required for unit tests


Ok convert it into readme.md so i can copy code please


### 🔐 JWT Security

This project uses JSON Web Tokens (JWT) for authentication and authorization across services.
- **Production & Runtime:** Uses **ES256**, an elliptic-curve–based asymmetric algorithm. Tokens are signed by the auth service using a private key and verified by other services using a public key, providing strong security and preventing token forgery.
- **Testing & CI:** Uses **HS256** to simplify setup and ensure fast, reliable automated testing.
This design balances strong production security with efficient local development and CI pipelines.

