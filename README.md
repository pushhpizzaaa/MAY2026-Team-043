# Servants of Bharat - Backend

This repository contains the backend source code for the **Servants of Bharat** volunteer platform.

## Tech Stack

- Python 3.11+
- Flask
- Flask-JWT-Extended
- SQLAlchemy
- PostgreSQL (Supabase) / SQLite
- bcrypt
- ReportLab
- Supabase Storage
- Flasgger (Swagger UI)

## Prerequisites

- Python 3.11 or later
- pip
- Virtual Environment (recommended)

## Installation

1. Clone the repository.


2. Navigate to the backend project directory.

```bash
cd MAY2026-Team-043/servants-of-india
```

> If you have already opened the `servants-of-india` folder, skip this step.

3. Create and activate a virtual environment.

```bash
python -m venv .venv
```

**Windows**

```bash
.venv\Scripts\activate
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

4. Install dependencies.

```bash
pip install -r requirements.txt
```

5. Configure environment variables.

```bash
cp .env.example .env
```

Update the `.env` file with the required configuration values.

6. Seed the database.

```bash
python seed.py
```

## Run the Application

Start the Flask server:

```bash
python -m app.app
```

The API will be available at:

```
http://localhost:5000
```

## API Documentation

After starting the server:

- **Swagger UI**

```
http://localhost:5000/api/docs
```

- **OpenAPI Specification**

```
http://localhost:5000/api/openapi.json
```

### Static Swagger Specification

A standalone Swagger / OpenAPI 3.0 file covering every endpoint on the platform
(Auth, Users, Categories, Events, Submissions, Reviews, Progress, Certificates,
Notifications, Admin) is checked in at
[`servants-of-india/docs/openapi.swagger.yaml`](servants-of-india/docs/openapi.swagger.yaml).

It needs no running server — paste it into [editor.swagger.io](https://editor.swagger.io)
or open it in any OpenAPI viewer. On top of the standard spec, every operation carries
two custom extensions:

| Extension | Contents |
|-----------|----------|
| `x-user-story` | The user story the endpoint implements |
| `x-error-handling` | The error cases and status codes that operation returns |

Use the live `/api/docs` endpoint for trying requests against a running server, and this
file for reviewing the contract offline.

## Testing

The project has two independent test suites.

### Automated API Tests (pytest)

The `servants-of-india/tests/` folder holds the automated API suite — 82 tests across
9 modules, one per feature area, covering every endpoint the platform serves.

Each run builds the Flask app against a throwaway SQLite database seeded with the five
service categories and one Super Admin, so the suite is self-contained: no running
server, no Supabase credentials, and no effect on your development database.

Run from the `servants-of-india` directory (the fixtures import the `app` package, so
the working directory matters):

```bash
cd MAY2026-Team-043/servants-of-india
pytest tests/
```

Useful variations:

```bash
pytest tests/ -v                        # one line per test
pytest tests/test_auth.py               # a single file
pytest tests/ -k "ownership or status"  # match test names
```

The folder mirrors the blueprint layout under `app/` — one test module per feature area:

```
servants-of-india/tests/
├── conftest.py                   # shared fixtures (see below)
├── test_auth.py                  # 10 tests
├── test_users.py                 # 15 tests
├── test_categories.py            #  2 tests
├── test_events.py                # 14 tests
├── test_submissions.py           # 11 tests
├── test_reviews.py               # 10 tests
├── test_progress.py              #  3 tests
├── test_certificates.py          # 10 tests
└── test_notifications_admin.py   #  7 tests
```

| File | Covers |
|------|--------|
| `tests/conftest.py` | Shared fixtures: temp-DB app, test client, user factory, JWT auth headers, category ids, event factory, proof-submission factory |
| `tests/test_auth.py` | Registration validation, login, blocked accounts, logout |
| `tests/test_users.py` | Profile read/update, password change, admin user management, status changes |
| `tests/test_categories.py` | Read-only category listing and its auth requirement |
| `tests/test_events.py` | Event create/list/get by id and slug, update, delete, ownership enforcement |
| `tests/test_submissions.py` | Proof upload and validation, duplicate/pending rules, review queue scoping, per-submission access |
| `tests/test_reviews.py` | Approve/reject ownership, double-review conflict, progress and notification side effects, resubmission |
| `tests/test_progress.py` | Initial state, volunteer-only access, progress reflecting an approval |
| `tests/test_certificates.py` | Generation gated on full completion, idempotency, listing, download, public verification |
| `tests/test_notifications_admin.py` | Notification listing and read-state ownership, admin stats scoping per role |

`pytest` is already pinned in `requirements.txt`, so step 4 of the installation
instructions above installs everything the suite needs.

A written test-case log for this suite — every case in
`[ API, Inputs, Expected output, Actual output, Result ]` form, plus the defects testing
uncovered and how they were fixed — is at
[`servants-of-india/docs/testcases.md`](servants-of-india/docs/testcases.md).

### Performance & Manual API Tests (JMeter)

JMeter test plans, manual test cases, and their execution results live in
`servants-of-india/Jmeter_Tests/`. That folder has its own documentation — see
[`Jmeter_Tests/API_TESTING_EXECUTION_PLAN.md`](servants-of-india/Jmeter_Tests/API_TESTING_EXECUTION_PLAN.md)
for prerequisites, backend setup, and how to run the plans from either the JMeter GUI or
the command line.

Unlike the pytest suite, the JMeter plans run against a live server, so the backend must
be seeded and started first.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (optional for local development) |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase API key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key |
| `JWT_SECRET_KEY` | Secret key for JWT authentication |
| `STORAGE_BACKEND` | `local` or `supabase` |
| `PORT` | Server port (default: 5000) |

## Project Structure

```
MAY2026-Team-043/
├── README.md
└── servants-of-india/
    ├── app/
    │   ├── app.py            # app factory + entrypoint + error handlers
    │   ├── config.py         # env-driven config
    │   ├── extensions.py     # db, jwt instances
    │   ├── models/           # 8 SQLAlchemy models + enums
    │   ├── services/         # storage, notifications, certificate PDF
    │   ├── utils/            # security, decorators (RBAC), validators, responses
    │   ├── docs/            # OpenAPI 3 spec + Swagger UI wiring
    │   ├── auth/  users/  categories/  events/  submissions/  reviews/
    │   ├── progress/  certificates/  notifications/  admin/   # one blueprint each
    ├── tests/                # pytest API suite — one module per feature area
    ├── docs/                 # static swagger yaml + written test-case log
    ├── Jmeter_Tests/         # JMeter plans + manual test cases (see its own README)
    ├── seed.py               # categories + first Super Admin
    ├── requirements.txt
    └── .env.example
```

## Features

- JWT Authentication
- Role-Based Access Control (RBAC)
- Volunteer Management
- Event Management
- Proof Submission & Review
- Progress Tracking
- PDF Certificate Generation
- Certificate Verification
- Notifications
- Swagger API Documentation
- Automated API Test Suite (pytest) & JMeter Performance Tests

## Project Status

This project is under active backend development. Features are implemented, tested, and reviewed before being promoted to the UAT and production branches.