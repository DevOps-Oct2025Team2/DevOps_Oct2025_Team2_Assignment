This repository explains how the team runs the project locally using a standardised setup, so that every developer, lecturer, and tester can run the system the same way.

At a high level:

The project consists of multiple Flask backend services (e.g. auth-service, file-service).

Each service has its own PostgreSQL database, started using Docker Compose.

Databases run inside Docker containers, so no one needs to install PostgreSQL manually.

Database schema (tables) are shared using migration files committed to Git — data is not shared.

Each developer has their own local data, but everyone uses the same schema.

Key Ideas Explained Simply
1. Docker is used to run databases

Docker Compose starts the databases (auth-db, file-db).

Everyone runs the same database version.

Data is stored in Docker volumes, so restarting containers does not delete data.

Data is only deleted if volumes are explicitly removed.

2. Each service is independent

Each backend service:

Has its own Flask app

Has its own database connection

Has its own tables (models)

Has its own migrations folder

This prevents services from interfering with each other.

3. Database tables are created using migrations (not manually)

Developers define tables using Python classes (models.py).

Flask-Migrate generates migration scripts (instructions).

These scripts are committed to Git.

Anyone else can recreate the same tables by running the migration commands.

This ensures:

Everyone’s database structure is identical

No one shares actual data

Setup is repeatable for markers and CI

4. Clear developer responsibilities

Auth-service developer owns auth tables and migrations

File-service developer owns file tables and migrations

Team members pull each other’s migrations and apply them locally

This avoids conflicts and confusion.

5. Sample users exist for local testing

A script is provided to insert sample users into the auth database.

Passwords are hashed.

The script is safe to re-run and does not duplicate users.

This helps with local development and testing.

File Service — User Dashboard (MVP)
Overview

The User Dashboard is part of the File Service backend.
It allows a logged-in user to retrieve a list of only their own uploaded files.

All ownership checks are enforced server-side to prevent data leakage between users.
This feature is implemented following Test-Driven Development (TDD) principles and is verified using automated backend tests.

Feature Description
Endpoint
GET /dashboard

Purpose

Display files uploaded by the authenticated user

Prevent access to files owned by other users

Return an empty list when the user has no files

Security & Access Rules (Acceptance Criteria)
AC-DASH-01 — Authorised Access

User must be authenticated

Valid request returns HTTP 200

AC-DASH-02 — Unauthorised Access Prevention

If the user is not authenticated:

Access is denied

HTTP 401 Unauthorized is returned

AC-DASH-03 — User Data Isolation (Security Critical)

Only files owned by the authenticated user are returned

Server enforces ownership checks

Client-side manipulation cannot expose other users’ data

Test failure results in pipeline failure

AC-DASH-04 — Empty State Handling

If the user has no uploaded files:

An empty list is returned

No errors occur

Authentication (Local Development)

For local development and testing, authentication is simulated using an HTTP header:

X-User-Id: <user_id>


Example:

X-User-Id: 1


This allows backend logic and security rules to be tested independently of the authentication service.

Dashboard Response Format
Example Response
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

Empty State
{
  "files": []
}

Automated Testing (Ownership Isolation)
What the Test Verifies

The automated backend test ensures that:

Multiple users can exist in the database

Each user can have files stored

When the dashboard logic is executed for User A:

Only User A’s files are returned

Files belonging to other users are never returned

This directly validates AC-DASH-03 (Security Critical).

Running the Tests Locally (Unit Tests)
Important Note

Unit tests are fully isolated and do not require Docker.
A temporary in-memory database is created automatically for each test run, so tests are fast and deterministic.

Run Tests (File Service)

From inside the file_service/ folder:

pytest

Expected Output
1 passed


If the test fails, it indicates a violation of dashboard ownership rules (AC-DASH-03).

Test Design Notes

Tests run using an in-memory database, not PostgreSQL

Each test run creates and destroys its own data automatically

No manual cleanup is needed

No production data is involved

Test failure will fail the CI pipeline


If the test fails, it indicates a violation of dashboard security or ownership rules.

Test Design Notes

Tests run against a local Docker database, not production

Existing database rows are cleared at the start of the test to ensure deterministic results

No real user or production data is involved

Test failure will fail the CI pipeline


****** How to test authentication unit testing ******
## Go inside auth-service folder
cd auth-service

## Install dependencies
pip install -r requirements.txt

> This installs:
> 
- Flask
- Flask-SQLAlchemy
- PyJWT
- cryptography (required for ES256)
- pytest
- psycopg2-binary

## Generate ES256 JWT keys (run ONCE)
docker run --rm -v${PWD}:/keys alpine/openssl \
  ecparam -name prime256v1 -genkey -noout -out /keys/ec_private.pem

docker run --rm -v${PWD}:/keys alpine/openssl \
  ec -in /keys/ec_private.pem -pubout -out /keys/ec_public.pem


After this step, you should see inside auth-service folder:
---
ec_private.pem
ec_public.pem
---
These files **must NOT be committed** to Git.
---

## 5️⃣ Set environment variables for JWT keys
### Windows (PowerShell)
$env:JWT_PRIVATE_KEY =Get-Content ec_private.pem-Raw
$env:JWT_PUBLIC_KEY =Get-Content ec_public.pem-Raw


## 6️⃣ Run unit tests
---
pytest -v
or 
pytest - python -m pytest -v
---

## Expected Output
========================= test session starts =========================
collected 7 items

tests/test_auth.py::test_login_success_admin PASSED
tests/test_auth.py::test_login_success_user PASSED
tests/test_auth.py::test_login_invalid_credentials PASSED
tests/test_auth.py::test_login_missing_fields PASSED

==================== 7 passed, warnings in <1s ====================