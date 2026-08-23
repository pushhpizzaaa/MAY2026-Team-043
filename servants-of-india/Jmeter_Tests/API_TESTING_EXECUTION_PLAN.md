# JMeter API Testing — Servants of Bharat

This folder contains JMeter test plans, manual test-case CSVs, and Python scripts to assert and merge run results.

All plans target the Flask API at **`http://localhost:5000`**.

---

## Prerequisites

| Requirement            | Notes                                                                                                              |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Apache JMeter 5.6+** | [Download JMeter](https://jmeter.apache.org/download_jmeter.cgi). GUI for interactive runs; CLI for CI/automation. |
| **Python 3.10+**       | Used by generator and merge scripts.                                                                               |
| **Running backend**    | Seed DB and start API before any JMeter run (see [Backend setup](#backend-setup)).                                 |
| **Java 8+**            | Required by JMeter.                                                                                                |

### Backend setup

From the repo root:

```bash
cd /MAY2026-Team-043/servants-of-india
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # configure Supabase / DB
python seed.py                  # 5 categories + Super Admin
python -m app.app               # http://localhost:5000
```

**Seeded admin (used by JMeter scripts):**

| Field    | Value             |
| -------- | ----------------- |
| Email    | `admin@sob.local` |
| Password | `Admin@12345`     |

Verify: `GET http://localhost:5000/api/health` → `{"success": true, "data": {"status": "ok"}}`

OpenAPI docs: `http://localhost:5000/api/docs`

---

## Folder layout

```
Jmeter_Tests/
├── API_TESTING_EXECUTION_PLAN.md                     ← this file
├── JMeter_Scripts/
│   ├── Servants_of_Bharat_API.jmx                    # Smoke: one thread group per API endpoint
│   ├── Servants_of_Bharat_API_TestCases.jmx          # Full manual suite: 72 test cases (TC-001…TC-072)
│   ├── Servants_of_Bharat_API_Positive_TestCases.jmx # Happy-path only: 36 test cases
│   ├── Servants_of_Bharat_Swagger_Contract.jmx       # OpenAPI schema contract: 28 cases (SC-001…SC-028)
│   ├── test-image.jpg                                # Multipart submission tests
│   └── test-image.gif                                # Wrong-extension rejection tests
├── TestCases/
│   ├── API_Manual_TestCases.csv                      # Source manual test definitions
│   ├── API_Manual_TestCases_Results.csv              # Raw JMeter output (full suite)
│   ├── API_Manual_TestCases_Updated.csv              # Merged results (full suite)
│   ├── Swagger_Contract_TestCases.csv
│   ├── Swagger_Contract_TestCases_Results.csv
│   └── Swagger_Contract_TestCases_Updated.csv
├── generate_testcase_jmx.py          # Regenerate full 72-case JMX
├── merge_testcase_results.py         # Merge full-suite results → Updated CSV
└── swagger_validation_rules.json     # Per-case expected HTTP code + JSON schema (SC-*)
```

---

## JMeter API testing (Servants of Bharat)

**Target**: live Flask API at http://localhost:5000 — requires a running server and a seeded database (python seed.py: 5 categories + Super Admin). Not in-process; hits the real HTTP stack and your configured DB (Postgres via .env).

**Fixtures**: per–thread-group setup via HTTP — login/register steps extract JWTs into JMeter vars (ADMIN_TOKEN, VOL_TOKEN, EM_TOKEN) and reuse them as Authorization: Bearer ${ADMIN_TOKEN}. Dynamic test data uses ${\_\_UUID()} emails; multipart flows attach Testing/JMeter_Scripts/test-image.jpg (or .gif for rejection tests).

## **Coverage**: four plans — endpoint smoke (Servants_of_Bharat_API.jmx), 72 manual cases (TC-001…072: success + validation + RBAC), 36 positive-only cases, and 28 OpenAPI contract checks (SC-001…028: HTTP status + JSON schema). Each testcase thread group asserts expected status code and body fragments; results land in _\_Results.csv and merge to _\_Updated.csv via merge_testcase_results.py.

## JMeter test plans (overview)

| JMX file                                        | Purpose                                                  | Cases           | Results file                                        |
| ----------------------------------------------- | -------------------------------------------------------- | --------------- | --------------------------------------------------- |
| `Servants_of_Bharat_API.jmx`                    | Quick endpoint smoke — hits each route once              | ~35 endpoints   | _(View Results Tree only)_                          |
| `Servants_of_Bharat_API_TestCases.jmx`          | Full functional manual tests — positive **and** negative | 72 (TC-001…072) | `API_Manual_TestCases_Results.csv`                  |
| `Servants_of_Bharat_API_Positive_TestCases.jmx` | Happy-path / success scenarios only                      | 36              | `API_Manual_TestCases_Positive_Usecase_Results.csv` |
| `Servants_of_Bharat_Swagger_Contract.jmx`       | OpenAPI response schema + HTTP status contract           | 28 (SC-001…028) | `Swagger_Contract_TestCases_Results.csv`            |

Each testcase-driven plan uses **one Thread Group per test case**, runs thread groups **serially**, and includes:

1. **Setup** — clears the results CSV header row
2. **Test thread groups** — HTTP steps + assertions + result recorder
3. **TearDown** — runs the matching Python merge script to produce the `*_Updated.csv` file

---

## Running tests

### Option A — JMeter GUI

1. Open JMeter → **File → Open** → select a `.jmx` from `JMeter_Scripts/`.
2. Confirm **HTTP Request Defaults** point to `localhost:5000`.
3. Click **Start** (green play).
4. Watch **View Results Tree** / **Summary Report** listeners.
5. After the run finishes, check the `TestCases/*_Results.csv` and `*_Updated.csv` files (TearDown merge runs automatically).

### Option B — CLI (non-GUI)

From the repo root (adjust paths for your OS):

```bash
# Full manual suite (72 cases)
jmeter -n -t Jmeter_Tests/JMeter_Scripts/Servants_of_Bharat_API_TestCases.jmx -l Testing/jmeter-full.jtl

# Positive use cases only (36 cases)
jmeter -n -t Jmeter_Tests/JMeter_Scripts/Servants_of_Bharat_API_Positive_TestCases.jmx -l Testing/jmeter-positive.jtl

# OpenAPI contract validation (28 cases)
jmeter -n -t Jmeter_Tests/JMeter_Scripts/Servants_of_Bharat_Swagger_Contract.jmx -l Testing/jmeter-swagger.jtl
```

Ensure `python` is on your PATH — TearDown merge scripts invoke Python.

---

## Test results CSV format

All testcase CSVs share the same columns:

| Column       | Description                                               |
| ------------ | --------------------------------------------------------- |
| `TestCaseId` | e.g. `TC-001`, `SC-006`                                   |
| `Scenario`   | Short title                                               |
| `Steps`      | Manual steps (pipe-separated in results)                  |
| `Expected`   | Expected HTTP status + response behaviour                 |
| `Input`      | Request body / auth / query summary                       |
| `Actual`     | `HTTP_CODE \| response body` (body truncated ~1000 chars) |
| `Status`     | `Pass`, `Fail`, or `Not Run`                              |
| `Comments`   | Notes from source test case                               |
| `RunTime`    | Sample time in ms                                         |

### Pass / Fail logic (manual suites)

Status is **not** tied to JMeter’s default HTTP success flag (which treats 4xx as failed). A case **Passes** when:

1. **HTTP status code** matches the expected code for the final step, **and**
2. **Body fragments** defined for that step appear in the response (e.g. `"Missing required fields"`, `"token"`, `"approved"`).

Expected 401/422/403 responses therefore Pass when the API returns the correct error — not Fail.

### Swagger contract suite (SC-\*)

Each case validates:

- Expected **HTTP status code**
- Response body against the **OpenAPI JSON schema** (embedded Groovy validator, no external deps)

Status = `Pass` when schema validation reports `OK` (including expected 4xx error responses).

---

## Result file workflow

```
Source CSV          JMeter run              Raw results              Merged output
──────────          ──────────              ─────────────            ──────────────
API_Manual_         Servants_of_Bharat_     API_Manual_TestCases_    API_Manual_TestCases_
TestCases.csv  ──►  API_TestCases.jmx  ──►  Results.csv         ──►  Updated.csv
                    (Setup clears CSV)      (one row per TC)         (all TCs + Status)

Swagger_Contract    Swagger_Contract        Swagger_Contract_        Swagger_Contract_
.csv           ──►  .jmx               ──►  Results.csv         ──►  Updated.csv
```

---

## Test assets

| File                            | Used by                                                          |
| ------------------------------- | ---------------------------------------------------------------- |
| `JMeter_Scripts/test-image.jpg` | TC-043, SC-017+, certificate/submission flows (multipart upload) |
| `JMeter_Scripts/test-image.gif` | TC-045 (invalid image extension)                                 |

Paths are embedded as absolute paths when JMX is generated. Re-run the generator if you move the repo.

---

## Suite details

### Full manual suite (TC-001 … TC-072)

Covers auth, users, categories, events, submissions, reviews, progress, certificates, notifications, admin stats — including **negative** cases (missing fields, forbidden roles, duplicate email, etc.).

Multi-step cases chain requests inside one thread group (e.g. admin login → create EM → create event → submit proof → approve).

### Positive use cases only

Subset where the final step expects **2xx** and the scenario is a happy path. Excludes invalid input, forbidden access, not-found, and similar error-path titles.

Current IDs: `TC-001, TC-002, TC-007, TC-011, TC-012, TC-014, TC-016, TC-019, TC-020, TC-022, TC-025, TC-028, TC-030, TC-034–036, TC-038, TC-040–041, TC-043, TC-048–051, TC-053, TC-055, TC-058, TC-060–062, TC-064, TC-066, TC-068–071`.

### Swagger contract suite (SC-001 … SC-028)

- Health, auth, users, events, submissions, certificates, admin, verify
- Success schemas (AuthResponse, Event, etc.)
- Error schema on 401 / 422
- Public verify endpoint

Rules per case are stored in `swagger_validation_rules.json`.

---

## Related documentation

- Test suite: `Jmeter_Tests/`
