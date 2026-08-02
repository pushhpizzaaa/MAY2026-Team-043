# Sprint 1 — API Test Cases

**Project:** Servants of Bharat · **Milestone 3 (Sprint 1)**
**Format:** `[ API being tested, Inputs, Expected output, Actual output, Result (Success/Fail) ]`
**Automated by:** `servants-of-india/tests/test_sprint1_*.py` (pytest) · **Result of last run: 41 passed.**

> "Actual output" below is the observed HTTP status/behaviour from the pytest run. Each row
> maps to a named test function so it is fully reproducible with `pytest -v`.

Run the suite:

```bash
cd servants-of-india
pytest tests/ -v
```

---

## 1. Auth — `/api/auth`  (`test_sprint1_auth.py`)

| API | Inputs | Expected output | Actual output | Result |
|-----|--------|-----------------|---------------|--------|
| POST /auth/register | Valid name, email, password≥8, phone, location | 201 + `{token, user{role:volunteer}}` | 201, volunteer user + token | Success |
| POST /auth/register | Missing phone & location | 422 "Missing required fields: phone, location" | 422 | Success |
| POST /auth/register | Password `"short"` (< 8) | 422 password too short | 422 | Success |
| POST /auth/register | Email `"not-an-email"` | 422 invalid email | 422 | Success |
| POST /auth/register | Email already registered | 409 conflict | 409 | Success |
| POST /auth/login | Correct admin email + password | 200 + `{token, user{role:super_admin}}` | 200, token issued | Success |
| POST /auth/login | Correct email, wrong password | 401 invalid credentials | 401 | Success |
| POST /auth/login | Unknown email | 401 invalid credentials | 401 | Success |
| POST /auth/login | Blocked account | 403 account blocked | 403 | Success |
| POST /auth/logout | Any request | 200 `{success:true}` | 200 | Success |

## 2. Users — `/api/users`  (`test_sprint1_users.py`)

| API | Inputs | Expected output | Actual output | Result |
|-----|--------|-----------------|---------------|--------|
| GET /users/me | Valid token | 200 + own profile | 200 | Success |
| GET /users/me | No Authorization header | 401 unauthorized | 401 | Success |
| PUT /users/me | Token + `{location:"Chennai"}` | 200 + updated profile | 200, location updated | Success |
| PUT /users/me/password | Correct current + new≥8 | 200 password updated | 200 | Success |
| PUT /users/me/password | **Wrong** current password | **400** (NOT 401 — no logout) | 400 | Success |
| PUT /users/me/password | New password < 8 | 422 too short | 422 | Success |
| GET /users | Admin token | 200 + list of users | 200 | Success |
| GET /users?role=event_manager | Admin token | 200 + only event managers | 200, filtered | Success |
| GET /users | Volunteer token | 403 forbidden | 403 | Success |
| POST /users | Admin + full EM body (org, phone, location) | 201 + event_manager | 201 | Success |
| POST /users | Admin + EM body **missing organization** | 422 org required | 422 | Success |
| POST /users | Volunteer token | 403 forbidden | 403 | Success |
| PATCH /users/{id}/status | Admin blocks another user | 200 + status "blocked" | 200 | Success |
| PATCH /users/{id}/status | Admin blocks **own** id | 400 cannot change own status | 400 | Success |
| PATCH /users/{id}/status | status = `"banana"` | 422 invalid status | 422 | Success |

## 3. Categories — `/api/categories`  (`test_sprint1_categories.py`)

| API | Inputs | Expected output | Actual output | Result |
|-----|--------|-----------------|---------------|--------|
| GET /categories | Valid token | 200 + exactly 5 categories | 200, 5 rows | Success |
| GET /categories | No token | 401 unauthorized | 401 | Success |

## 4. Events — `/api/events`  (`test_sprint1_events.py`)

| API | Inputs | Expected output | Actual output | Result |
|-----|--------|-----------------|---------------|--------|
| POST /events | EM token + valid body | 201 + event with readable slug | 201, slug `tree-plantation-drive-…` | Success |
| POST /events | Volunteer token + valid body | 403 forbidden | 403 | Success |
| POST /events | EM token, missing `title` | 422 missing field | 422 | Success |
| POST /events | EM token, invalid `category_id` | 422 invalid category | 422 | Success |
| POST /events | No Authorization header | 401 unauthorized | 401 | Success |
| GET /events | Valid token | 200 + list | 200 | Success |
| GET /events/{id} | Existing UUID | 200 + event | 200 | Success |
| GET /events/{slug} | Readable slug | 200 + same event | 200, resolved by slug | Success |
| GET /events/{id} | Unknown identifier | 404 not found | 404 | Success |
| PUT /events/{id} | Owner EM, `{status:"completed"}` | 200 + updated | 200 | Success |
| PUT /events/{id} | **Different** EM (not owner) | 403 not your event | 403 | Success |
| PUT /events/{id} | Super Admin (any event) | 200 + updated | 200 | Success |
| DELETE /events/{id} | Owner EM | 200 deleted | 200 | Success |
| DELETE /events/{id} | Different EM (not owner) | 403 not your event | 403 | Success |

---

## 5. Cases where Actual differed from Expected (defects found by testing → fixed)

These demonstrate how testing improved the API. Both were caught during Sprint 1 development
and corrected; the tests above now guard against regressions.

| API | Inputs | Expected output | Actual (before fix) | Fix | Result now |
|-----|--------|-----------------|---------------------|-----|-----------|
| PUT /users/me/password | Wrong current password | 400 + inline error, user stays logged in | **401** → frontend interceptor logged the user out | Return **400** instead of 401 for a wrong current password | Success |
| GET /api/docs (Swagger UI) | Open the docs page | Rendered API docs | "swagger and openapi fields cannot both be present" — UI blank | Force OpenAPI 3 in the Flasgger config so `swagger:"2.0"` is not emitted | Success |
| GET /submissions?status=pending *(EM)* | EM review queue, pending tab | Pending submissions for own events | **Empty** — after the join, `filter_by(status=)` bound to `Event.status` | Use explicit `Submission.status == status` | Success |

*(The third row is a Sprint 2 endpoint but the bug was found and fixed during Sprint 1
integration work; included as additional evidence.)*

---

## 6. Summary

| Group | Endpoints | Test cases | Passed |
|-------|-----------|-----------|--------|
| Auth | 3 | 10 | 10 |
| Users | 6 | 15 | 15 |
| Categories | 1 | 2 | 2 |
| Events | 5 | 14 | 14 |
| **Total** | **15** | **41** | **41** |

All 41 automated Sprint 1 test cases pass (`pytest tests/ -v`).
