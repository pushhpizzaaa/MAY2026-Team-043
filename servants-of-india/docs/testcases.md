# API Test Cases — Complete

**Project:** Servants of Bharat · **All API endpoints (Sprint 1 + Sprint 2)**
**Format:** `[ API being tested, Inputs, Expected output, Actual output, Result (Success/Fail) ]`
**Automated by:** `servants-of-india/tests/` (pytest) · **Result of last full run: 82 passed.**

Run the suite:

```bash
cd servants-of-india
pip install -r requirements.txt
pytest tests/ -v
```

Each test uses a throwaway SQLite database seeded with the five service categories and one
Super Admin, so every case is reproducible and isolated. The "Actual output" column below
reflects the observed behaviour from the passing run.

---

## 1. Auth — `/api/auth`  (`test_auth.py`)

| API | Inputs | Expected output | Actual output | Result |
|-----|--------|-----------------|---------------|--------|
| POST /auth/register | Valid name, email, password≥8, phone, location | 201 + `{token, user{role:volunteer}}` | 201, volunteer + token | Success |
| POST /auth/register | Missing phone & location | 422 "Missing required fields: phone, location" | 422 | Success |
| POST /auth/register | Password `"short"` (< 8) | 422 password too short | 422 | Success |
| POST /auth/register | Malformed email `"not-an-email"` | 422 invalid email | 422 | Success |
| POST /auth/register | Duplicate email | 409 email already registered | 409 | Success |
| POST /auth/login | Correct email + password | 200 + `{token, user{role}}` | 200 | Success |
| POST /auth/login | Correct email, wrong password | 401 invalid credentials | 401 | Success |
| POST /auth/login | Unknown email | 401 invalid credentials | 401 | Success |
| POST /auth/login | Blocked account | 403 account blocked | 403 | Success |
| POST /auth/logout | Any request | 200 `{success:true}` | 200 | Success |

## 2. Users — `/api/users`  (`test_users.py`)

| API | Inputs | Expected output | Actual output | Result |
|-----|--------|-----------------|---------------|--------|
| GET /users/me | Valid token | 200 + own profile | 200 | Success |
| GET /users/me | No Authorization header | 401 unauthorized | 401 | Success |
| PUT /users/me | Token + `{location:"Chennai"}` | 200 + updated profile | 200 | Success |
| PUT /users/me/password | Correct current + new≥8 | 200 password updated | 200 | Success |
| PUT /users/me/password | **Wrong** current password | **400** (NOT 401 — stays logged in) | 400 | Success |
| PUT /users/me/password | New password < 8 | 422 too short | 422 | Success |
| GET /users | Admin token | 200 + list of users | 200 | Success |
| GET /users?role=event_manager | Admin token | 200 + only event managers | 200 | Success |
| GET /users | Volunteer token | 403 forbidden | 403 | Success |
| POST /users | Admin + full EM body (org, phone, location) | 201 + event_manager | 201 | Success |
| POST /users | Admin + EM body **missing organization** | 422 org required | 422 | Success |
| POST /users | Volunteer token | 403 forbidden | 403 | Success |
| PATCH /users/{id}/status | Admin blocks another user | 200 + status "blocked" | 200 | Success |
| PATCH /users/{id}/status | Admin blocks **own** id | 400 cannot change own status | 400 | Success |
| PATCH /users/{id}/status | status = `"banana"` | 422 invalid status | 422 | Success |

## 3. Categories — `/api/categories`  (`test_categories.py`)

| API | Inputs | Expected output | Actual output | Result |
|-----|--------|-----------------|---------------|--------|
| GET /categories | Valid token | 200 + exactly 5 categories | 200, 5 rows | Success |
| GET /categories | No token | 401 unauthorized | 401 | Success |

## 4. Events — `/api/events`  (`test_events.py`)

| API | Inputs | Expected output | Actual output | Result |
|-----|--------|-----------------|---------------|--------|
| POST /events | EM token + valid body | 201 + event with readable slug | 201, slug present | Success |
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

## 5. Submissions — `/api/submissions`  (`test_submissions.py`)

| API | Inputs | Expected output | Actual output | Result |
|-----|--------|-----------------|---------------|--------|
| POST /submissions | Volunteer + image + category + completed event | 201 + submission `pending` | 201 | Success |
| POST /submissions | Event Manager token | 403 (only volunteers submit) | 403 | Success |
| POST /submissions | Missing `description` | 422 validation | 422 | Success |
| POST /submissions | Missing `image` | 422 validation | 422 | Success |
| POST /submissions | Second pending for same category | 409 duplicate pending | 409 | Success |
| POST /submissions | Category already approved | 409 category completed | 409 | Success |
| GET /submissions/me | Volunteer token | 200 + own submissions | 200 | Success |
| GET /submissions?status=pending | Owner EM sees own subs (1); a different EM sees none (0) | Owner list = 1, other EM list = 0 | 1 and 0 | Success |
| GET /submissions?status=pending | Volunteer token | 403 forbidden | 403 | Success |
| GET /submissions/{id} | Owning volunteer | 200 + submission | 200 | Success |
| GET /submissions/{id} | A different volunteer | 403 forbidden | 403 | Success |

## 6. Reviews — `/api/submissions/{id}`  (`test_reviews.py`)

| API | Inputs | Expected output | Actual output | Result |
|-----|--------|-----------------|---------------|--------|
| POST /submissions/{id}/approve | Owner EM | 200 + status `approved` | 200 | Success |
| POST /submissions/{id}/approve | Super Admin (any event) | 200 + approved | 200 | Success |
| POST /submissions/{id}/approve | **Different** EM (not owner) | 403 not your event | 403 | Success |
| POST /submissions/{id}/approve | Volunteer token | 403 forbidden | 403 | Success |
| POST /submissions/{id}/approve | Already-reviewed submission | 409 already reviewed | 409 | Success |
| POST /submissions/{id}/approve | (side effect) | Category progress → `completed` | completed_count = 1 | Success |
| POST /submissions/{id}/approve | (side effect) | Volunteer gets an `approval` notification | notification created | Success |
| POST /submissions/{id}/reject | No `remarks` | 422 remarks required | 422 | Success |
| POST /submissions/{id}/reject | `{remarks:"Photo unclear"}` | 200 + status `rejected` | 200 | Success |
| POST /submissions/{id}/reject | (then resubmit same category) | 201 — resubmission allowed | 201 | Success |

## 7. Progress — `/api/progress`  (`test_progress.py`)

| API | Inputs | Expected output | Actual output | Result |
|-----|--------|-----------------|---------------|--------|
| GET /progress/me | New volunteer | 200 + 5 categories all `not_started`, stars 0 | 200 | Success |
| GET /progress/me | Admin token | 403 (volunteers only) | 403 | Success |
| GET /progress/me | After one approval | `completed_count` = 1, `stars` = 1 | 200 | Success |

## 8. Certificates — `/api/certificates` & `/api/verify`  (`test_certificates.py`)

| API | Inputs | Expected output | Actual output | Result |
|-----|--------|-----------------|---------------|--------|
| POST /certificates/generate | Not all 5 categories completed | 400 blocked | 400 | Success |
| POST /certificates/generate | All 5 categories completed | 200 + cert (`SOB-YYYY-NNNNN` + code) | 200 | Success |
| POST /certificates/generate | Called again (idempotent) | Same certificate number returned | same number | Success |
| GET /certificates/me | After generation | 200 + certificate | 200 | Success |
| GET /certificates/me | Before any generation | 404 no certificate yet | 404 | Success |
| GET /certificates | Super Admin | 200 + all issued certificates | 200 | Success |
| GET /certificates | Volunteer token | 403 forbidden | 403 | Success |
| GET /certificates/{id}/download | Owner | 200 + `{download_url}` | 200 | Success |
| GET /verify/{code} | Valid verification code (no auth) | 200 + `valid:true` + summary | 200, valid true | Success |
| GET /verify/{code} | Unknown code (no auth) | 200 + `valid:false` | 200, valid false | Success |

## 9. Notifications & Admin — `/api/notifications`, `/api/admin`  (`test_notifications_admin.py`)

| API | Inputs | Expected output | Actual output | Result |
|-----|--------|-----------------|---------------|--------|
| GET /notifications | Volunteer with an approval | 200 + list + `unread_count`≥1 | 200 | Success |
| PATCH /notifications/{id}/read | Own notification | 200 + `is_read:true` | 200 | Success |
| PATCH /notifications/{id}/read | Another user's notification | 404 not found | 404 | Success |
| GET /notifications | No Authorization header | 401 unauthorized | 401 | Success |
| GET /admin/stats | Super Admin | 200 + `scope:"system"` + user/submission counts | 200 | Success |
| GET /admin/stats | Event Manager | 200 + `scope:"own"`, counts scoped to own events | 200, events=1, pending=1 | Success |
| GET /admin/stats | Volunteer token | 403 forbidden | 403 | Success |

---

## 10. Test cases where Actual differed from Expected (defects found → fixed)

These are real defects surfaced by testing/integration and then fixed. They demonstrate how
testing improves the implementation. The suite above now guards against each regression.

| API | Inputs | Expected | Actual (before fix) | Fix | Result now |
|-----|--------|----------|---------------------|-----|-----------|
| PUT /users/me/password | Wrong current password | 400 + inline error, stay logged in | **401** → frontend interceptor logged the user out | Return **400** (validation) instead of 401 | Success |
| GET /api/docs (Swagger UI) | Open the docs page | Rendered API docs | Blank — "swagger and openapi cannot both be present" | Force OpenAPI 3 in Flasgger config (drop `swagger:"2.0"`) | Success |
| GET /submissions?status=pending (EM) | EM review-queue "pending" tab | Pending submissions for own events | **Empty** — after join, `filter_by(status=)` bound to `Event.status` | Use explicit `Submission.status == status` | Success |

---

## 11. Summary

| Module | Endpoints | Test cases | Passed |
|--------|-----------|-----------|--------|
| Auth | 3 | 10 | 10 |
| Users | 6 | 15 | 15 |
| Categories | 1 | 2 | 2 |
| Events | 5 | 14 | 14 |
| Submissions | 4 | 11 | 11 |
| Reviews | 2 | 10 | 10 |
| Progress | 1 | 3 | 3 |
| Certificates | 5 | 10 | 10 |
| Notifications & Admin | 3 | 7 | 7 |
| **Total** | **30** | **82** | **82** |

All 82 automated test cases pass (`pytest tests/ -v`).
