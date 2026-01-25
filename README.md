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

All unit tests are fully isolated and do NOT require Docker or real databases.

Each service uses an isolated test environment:
- auth-service uses mocked dependencies and environment-injected secrets
- file-service uses an in-memory database

This ensures tests are fast, deterministic, and safe to run on any machine or CI runner.

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


Auth Service — Unit Testing

Overview

Auth-service unit tests are fully isolated and do not rely on:
- real databases
- real JWT key files
- Docker containers

All cryptographic dependencies are injected or mocked to ensure true unit testing.

Running Auth-Service Unit Tests

From inside the auth-service/ folder:

pip install -r requirements.txt
pytest -v

Environment Configuration

JWT signing and verification keys are provided via environment variables during testing.
No PEM files are read from disk during unit tests.

This allows tests to run safely in:
- local development environments
- CI runners
- isolated test contexts

Expected Output

========================= test session starts =========================
tests/test_auth.py::test_login_success_admin PASSED                                               [  7%]
tests/test_auth.py::test_login_success_user PASSED                                                [ 15%]
tests/test_auth.py::test_login_invalid_credentials[admin-wrong] PASSED                            [ 23%]
tests/test_auth.py::test_login_invalid_credentials[user1-wrong] PASSED                            [ 30%]
tests/test_auth.py::test_login_invalid_credentials[admin1-admin123] PASSED                        [ 38%]
tests/test_auth.py::test_login_invalid_credentials[user-user123] PASSED                           [ 46%]
tests/test_auth.py::test_login_missing_fields PASSED                                              [ 53%]
tests/test_auth.py::test_admin_access_without_token PASSED                                        [ 61%]
tests/test_auth.py::test_admin_access_denied_for_non_admin PASSED                                 [ 69%]
tests/test_auth.py::test_admin_access_allowed_for_admin PASSED                                    [ 76%] 
tests/test_auth.py::test_access_after_logout PASSED                                               [ 84%] 
tests/test_auth.py::test_login_returns_token_and_role PASSED                                      [ 92%] 
tests/test_auth.py::test_login_invalid_json_body PASSED                                           [100%] 

=========================================== warnings summary =========================================== 
tests/test_auth.py: 12 warnings
  C:\Users\yeyin\AppData\Roaming\Python\Python313\site-packages\sqlalchemy\sql\schema.py:3624: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return util.wrap_callable(lambda ctx: fn(), fn)  # type: ignore

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=================================== 13 passed, 12 warnings in 2.31s ====================================c

==================== all tests passed ====================

Design Notes

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
