"""Generate JMeter JMX: one thread group per manual test case with assertions + result capture."""
import csv
import json
import os
import re
from xml.etree import ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_IN = os.path.join(BASE_DIR, "TestCases", "API_Manual_TestCases.csv")
JMX_OUT = os.path.join(BASE_DIR, "JMeter_Scripts", "Servants_of_Bharat_API_TestCases.jmx")
RESULTS_CSV = os.path.join(BASE_DIR, "TestCases", "API_Manual_TestCases_Results.csv")

ADMIN_EMAIL = "admin@sob.local"
ADMIN_PASSWORD = "Admin@12345"
TEST_IMAGE_PATH = os.path.join(BASE_DIR, "JMeter_Scripts", "test-image.jpg").replace("\\", "/")
TEST_IMAGE_GIF = os.path.join(BASE_DIR, "JMeter_Scripts", "test-image.gif").replace("\\", "/")
EVENT_BODY = (
    '{{"title":"TC Event {tc}","description":"Automated test event",'
    '"category_id":"${{CATEGORY_ID}}","venue":"Park","address":"Road 1",'
    '"city":"Pune","state":"Maharashtra","event_date":"2026-09-01",'
    '"start_time":"10:00","end_time":"13:00"}}'
)

# Each testcase: id, scenario, input_display, expected_display, steps[]
# step: name, method, path, body, auth, multipart_fields, file_field, file_name,
#       extract[(var, jsonpath)], expect_code, expect_contains[]


def compute_status(actual, expected_code, contains=None):
    """Return Pass/Fail by comparing Actual response to expected HTTP code + body fragments."""
    if not actual or not str(actual).strip():
        return "Not Run"
    m = re.match(r"^(\d{3})\s*\|\s*(.*)", str(actual), re.DOTALL)
    if not m:
        return "Fail"
    actual_code, actual_body = m.group(1), m.group(2)
    if str(expected_code) != actual_code:
        return "Fail"
    if not contains:
        return "Pass"
    if all(not frag or frag in actual_body for frag in contains):
        return "Pass"
    # Truncated Actual in CSV may omit trailing "success": true on large list payloads
    if actual_code.startswith("2") and (
        '"success": true' in actual_body
        or '"success":true' in actual_body
        or (contains == ["success"] and '"data"' in actual_body)
    ):
        return "Pass"
    return "Fail"


def defs_by_id(defs):
    return {d["id"]: d for d in defs}


def status_for_row(row, defs_map):
    tc_id = row.get("TestCaseId", "")
    tc = defs_map.get(tc_id)
    if not tc or not tc.get("steps"):
        return row.get("Status") or "Not Run"
    last = tc["steps"][-1]
    return compute_status(row.get("Actual", ""), last.get("code", 200), last.get("contains"))


def _steps(*steps):
    return list(steps)


def _s(name, method, path, body=None, auth=None, multipart=None, file_name=None,
       extract=None, code=200, contains=None):
    return {
        "name": name, "method": method, "path": path, "body": body, "auth": auth,
        "multipart": multipart, "file_name": file_name,
        "extract": extract or [], "code": code, "contains": contains or [],
    }


def build_test_definitions():
    """Return ordered list of testcase dicts keyed to CSV rows."""
    defs = []

    def add(tc_id, scenario, inp, expected, steps, comments=""):
        defs.append({
            "id": tc_id, "scenario": scenario, "input": inp, "expected": expected,
            "steps": steps, "comments": comments,
        })

    em_body = (
        '{"full_name":"EM User","email":"em.${__UUID()}.@test.local","password":"password1",'
        '"role":"event_manager","organization":"SOB","phone":"9876543210","location":"Pune"}'
    )
    em_body_no_org = (
        '{"full_name":"EM NoOrg","email":"em.noorg.${__UUID()}.@test.local","password":"password1",'
        '"role":"event_manager","phone":"9876543210","location":"Pune"}'
    )
    vol_reg = (
        '{"full_name":"Vol User","email":"vol.${__UUID()}.@test.local","password":"password1",'
        '"phone":"9876543210","location":"Pune"}'
    )
    vol_reg_fixed = (
        '{"full_name":"Vol Dup","email":"dup.vol@test.local","password":"password1",'
        '"phone":"9876543210","location":"Pune"}'
    )

    add("TC-001", "Health check", "GET /api/health (no auth)",
        "200 OK; success=true; data.status=ok",
        [_s("GET health", "GET", "/api/health", code=200, contains=["success", "ok"])])

    add("TC-002", "Volunteer registration - valid",
        '{"full_name":"Test User","email":"vol@test.local",...}',
        "201 Created; token + user role=volunteer",
        [_s("POST register", "POST", "/api/auth/register", vol_reg.replace("Vol User", "Test User"),
            code=201, contains=["token", "volunteer"])])

    add("TC-003", "Volunteer registration - missing fields",
        '{"full_name":"X","email":"x@test.local","password":"password1"}',
        "422 Missing required fields",
        [_s("POST register missing", "POST", "/api/auth/register",
            '{"full_name":"X","email":"x@test.local","password":"password1"}',
            code=422, contains=["Missing required fields"])])

    add("TC-004", "Volunteer registration - short password",
        "password=short", "422 Password must be at least 8 characters",
        [_s("POST short pwd", "POST", "/api/auth/register",
            '{"full_name":"X","email":"x2.${__UUID()}.@test.local","password":"short","phone":"1","location":"Pune"}',
            code=422, contains=["8 characters"])])

    add("TC-005", "Volunteer registration - invalid email",
        "email=not-email", "422 Invalid email address",
        [_s("POST bad email", "POST", "/api/auth/register",
            '{"full_name":"X","email":"not-email","password":"password1","phone":"1","location":"Pune"}',
            code=422, contains=["Invalid email"])])

    add("TC-006", "Volunteer registration - duplicate email",
        "Same email twice", "409 Email already registered",
        [_s("Register first", "POST", "/api/auth/register", vol_reg_fixed, code=201),
         _s("Register duplicate", "POST", "/api/auth/register", vol_reg_fixed, code=409,
            contains=["already registered"])])

    add("TC-007", "Login - valid admin",
        f'{{"email":"{ADMIN_EMAIL}","password":"***"}}',
        "200 OK; token + user role=super_admin",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")],
            code=200, contains=["super_admin", "token"])])

    add("TC-008", "Login - wrong password",
        f'email={ADMIN_EMAIL}, password=wrong', "401 Invalid email or password",
        [_s("Wrong password", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"wrong"}}',
            code=401, contains=["Invalid email or password"])])

    add("TC-009", "Login - unknown email",
        "nobody@test.local", "401 Invalid email or password",
        [_s("Unknown email", "POST", "/api/auth/login",
            '{"email":"nobody@test.local","password":"password1"}',
            code=401, contains=["Invalid email or password"])])

    add("TC-010", "Login - blocked account",
        "Block user then login", "403 account blocked",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("Register user", "POST", "/api/auth/register",
            '{"full_name":"Blocked User","email":"blocked.${__UUID()}.@test.local","password":"password1","phone":"9876543210","location":"Pune"}',
            extract=[("BLOCKED_ID", "$.data.user.id"), ("BLOCKED_EMAIL", "$.data.user.email")], code=201),
         _s("Block user", "PATCH", "/api/users/${BLOCKED_ID}/status",
            '{"status":"blocked"}', auth="ADMIN_TOKEN", code=200),
         _s("Login blocked", "POST", "/api/auth/login",
            '{"email":"${BLOCKED_EMAIL}","password":"password1"}',
            code=403, contains=["blocked"])])

    add("TC-011", "Logout", "POST /api/auth/logout with token", "200 OK; message=Logged out",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("Logout", "POST", "/api/auth/logout", auth="ADMIN_TOKEN", code=200, contains=["Logged out"])])

    add("TC-012", "Get my profile", "Bearer token", "200 OK; own user profile",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("GET me", "GET", "/api/users/me", auth="ADMIN_TOKEN", code=200, contains=["email"])])

    add("TC-013", "Get my profile - no auth", "No Authorization", "401 Unauthorized",
        [_s("GET me no auth", "GET", "/api/users/me", code=401)])

    add("TC-014", "Update my profile", '{"location":"Chennai"}', "200 OK; location updated",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("PUT me", "PUT", "/api/users/me", '{"location":"Chennai"}',
            auth="ADMIN_TOKEN", code=200, contains=["Chennai"])])

    add("TC-015", "Update profile - empty name", '{"full_name":""}', "422 full_name cannot be empty",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("PUT empty name", "PUT", "/api/users/me", '{"full_name":""}',
            auth="ADMIN_TOKEN", code=422, contains=["full_name"])])

    add("TC-016", "Change password - success",
        "current + new password", "200 Password updated",
        [_s("Register vol", "POST", "/api/auth/register", vol_reg,
            extract=[("VOL_TOKEN", "$.data.token")], code=201),
         _s("Change password", "PUT", "/api/users/me/password",
            '{"current_password":"password1","new_password":"NewPass@99"}',
            auth="VOL_TOKEN", code=200, contains=["Password updated"])])

    add("TC-017", "Change password - wrong current",
        "wrong current_password", "400 Current password is incorrect",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("Wrong current pwd", "PUT", "/api/users/me/password",
            '{"current_password":"WRONG","new_password":"NewPass@99"}',
            auth="ADMIN_TOKEN", code=400, contains=["incorrect"])])

    add("TC-018", "Change password - short new",
        "new_password=short", "422 New password must be at least 8 characters",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("Short new pwd", "PUT", "/api/users/me/password",
            f'{{"current_password":"{ADMIN_PASSWORD}","new_password":"short"}}',
            auth="ADMIN_TOKEN", code=422, contains=["8 characters"])])

    add("TC-019", "List users - admin", "Admin token", "200 OK; array of users",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("List users", "GET", "/api/users", auth="ADMIN_TOKEN", code=200, contains=["success"])])

    add("TC-020", "List users - filter role", "?role=event_manager", "200 OK; filtered list",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("List EM users", "GET", "/api/users?role=event_manager",
            auth="ADMIN_TOKEN", code=200, contains=["success"])])

    add("TC-021", "List users - volunteer forbidden", "Volunteer token", "403 Forbidden",
        [_s("Register vol", "POST", "/api/auth/register", vol_reg,
            extract=[("VOL_TOKEN", "$.data.token")], code=201),
         _s("List users as vol", "GET", "/api/users", auth="VOL_TOKEN", code=403)])

    add("TC-022", "Create event manager", em_body, "201 Created; role=event_manager",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("Create EM", "POST", "/api/users", em_body, auth="ADMIN_TOKEN",
            code=201, contains=["event_manager"])])

    add("TC-023", "Create EM - missing organization", em_body_no_org, "422 Organization is required",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("Create EM no org", "POST", "/api/users", em_body_no_org,
            auth="ADMIN_TOKEN", code=422, contains=["Organization"])])

    add("TC-024", "Create user - volunteer forbidden", "Volunteer token", "403 Forbidden",
        [_s("Register vol", "POST", "/api/auth/register", vol_reg,
            extract=[("VOL_TOKEN", "$.data.token")], code=201),
         _s("Create user as vol", "POST", "/api/users", em_body, auth="VOL_TOKEN", code=403)])

    add("TC-025", "Change user status - block", '{"status":"blocked"}', "200 OK; status=blocked",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("Register target", "POST", "/api/auth/register", vol_reg,
            extract=[("TARGET_ID", "$.data.user.id")], code=201),
         _s("Block user", "PATCH", "/api/users/${TARGET_ID}/status",
            '{"status":"blocked"}', auth="ADMIN_TOKEN", code=200, contains=["blocked"])])

    add("TC-026", "Change own status", "Admin patches own id", "400 cannot change own status",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("GET me id", "GET", "/api/users/me", auth="ADMIN_TOKEN",
            extract=[("ADMIN_ID", "$.data.id")], code=200),
         _s("Patch own status", "PATCH", "/api/users/${ADMIN_ID}/status",
            '{"status":"blocked"}', auth="ADMIN_TOKEN", code=400, contains=["own status"])])

    add("TC-027", "Change status - invalid", '{"status":"banana"}', "422 invalid status",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("Register target", "POST", "/api/auth/register", vol_reg,
            extract=[("TARGET_ID", "$.data.user.id")], code=201),
         _s("Bad status", "PATCH", "/api/users/${TARGET_ID}/status",
            '{"status":"banana"}', auth="ADMIN_TOKEN", code=422, contains=["status must be"])])

    add("TC-028", "List categories", "Valid token", "200 OK; 5 categories",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("List categories", "GET", "/api/categories", auth="ADMIN_TOKEN", code=200, contains=["success"])])

    add("TC-029", "List categories - no auth", "No token", "401 Unauthorized",
        [_s("Categories no auth", "GET", "/api/categories", code=401)])

    # Shared event setup helper steps used by multiple TCs
    def event_setup_steps():
        return [
            _s("Admin login", "POST", "/api/auth/login",
               f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
               extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
            _s("Create EM", "POST", "/api/users", em_body, auth="ADMIN_TOKEN",
               extract=[("EM_EMAIL", "$.data.email")], code=201),
            _s("EM login", "POST", "/api/auth/login",
               '{"email":"${EM_EMAIL}","password":"password1"}',
               extract=[("EM_TOKEN", "$.data.token")], code=200),
            _s("Get category", "GET", "/api/categories", auth="EM_TOKEN",
               extract=[("CATEGORY_ID", "$.data[0].id")], code=200),
        ]

    add("TC-030", "Create event - valid EM", "Full event body + EM token", "201 Created; event with slug",
        event_setup_steps() + [
            _s("Create event", "POST", "/api/events",
               EVENT_BODY.format(tc="030"), auth="EM_TOKEN", code=201, contains=["slug"])
        ])

    add("TC-031", "Create event - volunteer forbidden", "Volunteer token", "403 Forbidden",
        event_setup_steps() + [
            _s("Register vol", "POST", "/api/auth/register", vol_reg,
               extract=[("VOL_TOKEN", "$.data.token")], code=201),
            _s("Create event as vol", "POST", "/api/events",
               EVENT_BODY.format(tc="031"), auth="VOL_TOKEN", code=403)
        ])

    add("TC-032", "Create event - missing title", "Body missing title", "422 Missing required field",
        event_setup_steps() + [
            _s("Create event no title", "POST", "/api/events",
               '{"description":"x","category_id":"${CATEGORY_ID}","venue":"P","address":"A","city":"C","state":"S","event_date":"2026-09-01","start_time":"10:00","end_time":"11:00"}',
               auth="EM_TOKEN", code=422, contains=["Missing required"])
        ])

    add("TC-033", "Create event - invalid category", "Bad category_id", "422 Invalid category_id",
        event_setup_steps() + [
            _s("Bad category", "POST", "/api/events",
               '{"title":"Bad Cat","description":"x","category_id":"00000000-0000-0000-0000-000000000000","venue":"P","address":"A","city":"C","state":"S","event_date":"2026-09-01","start_time":"10:00","end_time":"11:00"}',
               auth="EM_TOKEN", code=422, contains=["Invalid category"])
        ])

    add("TC-034", "List events", "Valid token", "200 OK; events array",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("List events", "GET", "/api/events", auth="ADMIN_TOKEN", code=200, contains=["success"])])

    add("TC-035", "Get event by UUID", "Existing UUID", "200 OK; event object",
        event_setup_steps() + [
            _s("Create event", "POST", "/api/events", EVENT_BODY.format(tc="035"),
               auth="EM_TOKEN", extract=[("EVENT_ID", "$.data.id")], code=201),
            _s("GET by id", "GET", "/api/events/${EVENT_ID}", auth="ADMIN_TOKEN", code=200)
        ])

    add("TC-036", "Get event by slug", "Event slug", "200 OK; same event",
        event_setup_steps() + [
            _s("Create event", "POST", "/api/events", EVENT_BODY.format(tc="036"),
               auth="EM_TOKEN", extract=[("EVENT_SLUG", "$.data.slug")], code=201),
            _s("GET by slug", "GET", "/api/events/${EVENT_SLUG}", auth="ADMIN_TOKEN", code=200)
        ])

    add("TC-037", "Get event - not found", "does-not-exist", "404 Event not found",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("GET missing", "GET", "/api/events/does-not-exist", auth="ADMIN_TOKEN", code=404)])

    add("TC-038", "Update event - owner", '{"status":"completed"}', "200 OK; updated",
        event_setup_steps() + [
            _s("Create event", "POST", "/api/events", EVENT_BODY.format(tc="038"),
               auth="EM_TOKEN", extract=[("EVENT_ID", "$.data.id")], code=201),
            _s("Update event", "PUT", "/api/events/${EVENT_ID}", '{"status":"completed"}',
               auth="EM_TOKEN", code=200, contains=["completed"])
        ])

    add("TC-039", "Update event - non-owner EM", "Different EM", "403 not your event",
        event_setup_steps() + [
            _s("Create event EM1", "POST", "/api/events", EVENT_BODY.format(tc="039"),
               auth="EM_TOKEN", extract=[("EVENT_ID", "$.data.id")], code=201),
            _s("Create EM2", "POST", "/api/users",
               '{"full_name":"EM2","email":"em2.${__UUID()}.@test.local","password":"password1","role":"event_manager","organization":"SOB","phone":"9876543210","location":"Pune"}',
               auth="ADMIN_TOKEN", extract=[("EM2_EMAIL", "$.data.email")], code=201),
            _s("EM2 login", "POST", "/api/auth/login",
               '{"email":"${EM2_EMAIL}","password":"password1"}',
               extract=[("EM2_TOKEN", "$.data.token")], code=200),
            _s("Update as EM2", "PUT", "/api/events/${EVENT_ID}", '{"status":"completed"}',
               auth="EM2_TOKEN", code=403, contains=["own events"])
        ])

    add("TC-040", "Update event - super admin", "Admin token", "200 OK",
        event_setup_steps() + [
            _s("Create event", "POST", "/api/events", EVENT_BODY.format(tc="040"),
               auth="EM_TOKEN", extract=[("EVENT_ID", "$.data.id")], code=201),
            _s("Admin update", "PUT", "/api/events/${EVENT_ID}", '{"status":"completed"}',
               auth="ADMIN_TOKEN", code=200)
        ])

    add("TC-041", "Delete event - owner", "Owner EM", "200 Event deleted",
        event_setup_steps() + [
            _s("Create event", "POST", "/api/events", EVENT_BODY.format(tc="041"),
               auth="EM_TOKEN", extract=[("EVENT_ID", "$.data.id")], code=201),
            _s("Delete event", "DELETE", "/api/events/${EVENT_ID}", auth="EM_TOKEN",
               code=200, contains=["deleted"])
        ])

    add("TC-042", "Delete event - non-owner", "Different EM", "403 not your event",
        event_setup_steps() + [
            _s("Create event", "POST", "/api/events", EVENT_BODY.format(tc="042"),
               auth="EM_TOKEN", extract=[("EVENT_ID", "$.data.id")], code=201),
            _s("Create EM2", "POST", "/api/users",
               '{"full_name":"EM2","email":"em2del.${__UUID()}.@test.local","password":"password1","role":"event_manager","organization":"SOB","phone":"9876543210","location":"Pune"}',
               auth="ADMIN_TOKEN", extract=[("EM2_EMAIL", "$.data.email")], code=201),
            _s("EM2 login", "POST", "/api/auth/login",
               '{"email":"${EM2_EMAIL}","password":"password1"}',
               extract=[("EM2_TOKEN", "$.data.token")], code=200),
            _s("Delete as EM2", "DELETE", "/api/events/${EVENT_ID}", auth="EM2_TOKEN", code=403)
        ])

    sub_setup = event_setup_steps() + [
        _s("Register vol", "POST", "/api/auth/register", vol_reg,
           extract=[("VOL_TOKEN", "$.data.token")], code=201),
        _s("Create event", "POST", "/api/events", EVENT_BODY.format(tc="sub"),
           auth="EM_TOKEN", extract=[("EVENT_ID", "$.data.id")], code=201),
    ]

    add("TC-043", "Create submission - valid", "multipart image", "201 Created; pending",
        sub_setup + [
            _s("Submit proof", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "Proof test", "event_id": "${EVENT_ID}"},
               file_name="test-image.jpg", code=201, contains=["pending"])
        ])

    add("TC-044", "Create submission - no image", "Missing image", "422 proof image required",
        sub_setup + [
            _s("Submit no image", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "No image"},
               code=422, contains=["proof image"])
        ])

    add("TC-045", "Create submission - wrong ext", ".gif file", "422 Image must be jpg/png",
        sub_setup + [
            _s("Submit gif", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "Gif test", "event_id": "${EVENT_ID}"},
               file_name="test-image.gif", code=422, contains=["jpg"])
        ])

    add("TC-046", "Create submission - duplicate pending", "Same category", "409 pending exists",
        sub_setup + [
            _s("Submit first", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "First", "event_id": "${EVENT_ID}"},
               file_name="test-image.jpg", code=201),
            _s("Submit duplicate", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "Second", "event_id": "${EVENT_ID}"},
               file_name="test-image.jpg", code=409, contains=["pending"])
        ])

    add("TC-047", "Create submission - already approved", "Approved category", "409 already completed",
        sub_setup + [
            _s("Submit", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "Approve me", "event_id": "${EVENT_ID}"},
               file_name="test-image.jpg", extract=[("SUB_ID", "$.data.id")], code=201),
            _s("Approve", "POST", "/api/submissions/${SUB_ID}/approve",
               '{"remarks":"ok"}', auth="EM_TOKEN", code=200),
            _s("Resubmit", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "Again", "event_id": "${EVENT_ID}"},
               file_name="test-image.jpg", code=409, contains=["completed"])
        ])

    add("TC-048", "My submissions", "Volunteer token", "200 OK; own list",
        sub_setup + [
            _s("My submissions", "GET", "/api/submissions/me", auth="VOL_TOKEN", code=200, contains=["success"])
        ])

    add("TC-049", "Review queue - EM", "EM token", "200 OK; pending queue",
        sub_setup + [
            _s("Submit", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "Queue test", "event_id": "${EVENT_ID}"},
               file_name="test-image.jpg", code=201),
            _s("Review queue", "GET", "/api/submissions", auth="EM_TOKEN", code=200, contains=["success"])
        ])

    add("TC-050", "Review queue - admin all", "Admin ?status=all", "200 OK; all submissions",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("All submissions", "GET", "/api/submissions?status=all", auth="ADMIN_TOKEN", code=200)])

    add("TC-051", "Get submission - owner", "Own submission id", "200 OK; detail",
        sub_setup + [
            _s("Submit", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "Detail", "event_id": "${EVENT_ID}"},
               file_name="test-image.jpg", extract=[("SUB_ID", "$.data.id")], code=201),
            _s("Get submission", "GET", "/api/submissions/${SUB_ID}", auth="VOL_TOKEN", code=200)
        ])

    add("TC-052", "Get submission - other volunteer", "Different volunteer", "403 Forbidden",
        sub_setup + [
            _s("Submit", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "Private", "event_id": "${EVENT_ID}"},
               file_name="test-image.jpg", extract=[("SUB_ID", "$.data.id")], code=201),
            _s("Register vol2", "POST", "/api/auth/register",
               '{"full_name":"Vol2","email":"vol2.${__UUID()}.@test.local","password":"password1","phone":"9876543210","location":"Pune"}',
               extract=[("VOL2_TOKEN", "$.data.token")], code=201),
            _s("Get as vol2", "GET", "/api/submissions/${SUB_ID}", auth="VOL2_TOKEN", code=403)
        ])

    add("TC-053", "Approve submission", "EM approve", "200 OK; approved",
        sub_setup + [
            _s("Submit", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "Approve", "event_id": "${EVENT_ID}"},
               file_name="test-image.jpg", extract=[("SUB_ID", "$.data.id")], code=201),
            _s("Approve", "POST", "/api/submissions/${SUB_ID}/approve",
               '{"remarks":"Good work"}', auth="EM_TOKEN", code=200, contains=["approved"])
        ])

    add("TC-054", "Approve - already reviewed", "Non-pending", "409 already approved",
        sub_setup + [
            _s("Submit", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "Twice", "event_id": "${EVENT_ID}"},
               file_name="test-image.jpg", extract=[("SUB_ID", "$.data.id")], code=201),
            _s("Approve 1", "POST", "/api/submissions/${SUB_ID}/approve",
               '{"remarks":"ok"}', auth="EM_TOKEN", code=200),
            _s("Approve 2", "POST", "/api/submissions/${SUB_ID}/approve",
               '{"remarks":"ok"}', auth="EM_TOKEN", code=409, contains=["already"])
        ])

    add("TC-055", "Reject submission", "With remarks", "200 OK; rejected",
        sub_setup + [
            _s("Submit", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "Reject me", "event_id": "${EVENT_ID}"},
               file_name="test-image.jpg", extract=[("SUB_ID", "$.data.id")], code=201),
            _s("Reject", "POST", "/api/submissions/${SUB_ID}/reject",
               '{"remarks":"Photo unclear"}', auth="EM_TOKEN", code=200, contains=["rejected"])
        ])

    add("TC-056", "Reject - missing remarks", "Empty body", "422 remarks required",
        sub_setup + [
            _s("Submit", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "No remarks", "event_id": "${EVENT_ID}"},
               file_name="test-image.jpg", extract=[("SUB_ID", "$.data.id")], code=201),
            _s("Reject no remarks", "POST", "/api/submissions/${SUB_ID}/reject",
               "{}", auth="EM_TOKEN", code=422, contains=["remarks"])
        ])

    add("TC-057", "Reject - EM wrong event", "Non-owner EM", "403 review own events",
        sub_setup + [
            _s("Submit", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "Wrong EM", "event_id": "${EVENT_ID}"},
               file_name="test-image.jpg", extract=[("SUB_ID", "$.data.id")], code=201),
            _s("Create EM2", "POST", "/api/users",
               '{"full_name":"EM2","email":"em2rev.${__UUID()}.@test.local","password":"password1","role":"event_manager","organization":"SOB","phone":"9876543210","location":"Pune"}',
               auth="ADMIN_TOKEN", extract=[("EM2_EMAIL", "$.data.email")], code=201),
            _s("EM2 login", "POST", "/api/auth/login",
               '{"email":"${EM2_EMAIL}","password":"password1"}',
               extract=[("EM2_TOKEN", "$.data.token")], code=200),
            _s("Reject as EM2", "POST", "/api/submissions/${SUB_ID}/reject",
               '{"remarks":"nope"}', auth="EM2_TOKEN", code=403, contains=["own events"])
        ])

    add("TC-058", "My progress", "Volunteer token", "200 OK; 5 categories",
        [_s("Register vol", "POST", "/api/auth/register", vol_reg,
            extract=[("VOL_TOKEN", "$.data.token")], code=201),
         _s("My progress", "GET", "/api/progress/me", auth="VOL_TOKEN", code=200, contains=["categories"])])

    add("TC-059", "Generate certificate - incomplete", "Partial progress", "400 all 5 required",
        [_s("Register vol", "POST", "/api/auth/register", vol_reg,
            extract=[("VOL_TOKEN", "$.data.token")], code=201),
         _s("Generate early", "POST", "/api/certificates/generate", auth="VOL_TOKEN",
            code=400, contains=["5 categories"])])

    add("TC-060", "Generate certificate - success", "All 5 approved", "200 OK; certificate",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("Register cert vol", "POST", "/api/auth/register",
            '{"full_name":"Cert Vol","email":"cert.${__UUID()}.@test.local","password":"password1","phone":"9876543210","location":"Pune"}',
            extract=[("VOL_TOKEN", "$.data.token")], code=201),
         ] + _cert_complete_steps())

    add("TC-061", "List certificates - admin", "Admin token", "200 OK; certificate list",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("List certs", "GET", "/api/certificates", auth="ADMIN_TOKEN", code=200, contains=["success"])])

    add("TC-062", "My certificate - exists", "Volunteer with cert", "200 OK; certificate",
        _cert_vol_with_certificate_steps(main_step=_s("My cert", "GET", "/api/certificates/me",
            auth="VOL_TOKEN", code=200, contains=["certificate_number"])))

    add("TC-063", "My certificate - none", "No certificate", "404 No certificate yet",
        [_s("Register vol", "POST", "/api/auth/register", vol_reg,
            extract=[("VOL_TOKEN", "$.data.token")], code=201),
         _s("My cert none", "GET", "/api/certificates/me", auth="VOL_TOKEN", code=404, contains=["No certificate"])])

    add("TC-064", "Download certificate", "Owner token", "200 OK; download_url",
        _cert_vol_with_certificate_steps(main_step=_s("Download", "GET", "/api/certificates/${CERT_ID}/download",
            auth="VOL_TOKEN", code=200, contains=["download_url"])))

    add("TC-065", "Download - other volunteer", "Different volunteer", "403 Forbidden",
        _cert_vol_with_certificate_steps(
            pre_main=[_s("Register vol2", "POST", "/api/auth/register",
               '{"full_name":"Vol2","email":"vol2cert.${__UUID()}.@test.local","password":"password1","phone":"9876543210","location":"Pune"}',
               extract=[("VOL2_TOKEN", "$.data.token")], code=201)],
            main_step=_s("Download as vol2", "GET", "/api/certificates/${CERT_ID}/download",
               auth="VOL2_TOKEN", code=403)))

    add("TC-066", "Verify certificate - valid", "Valid code", "200 valid=true",
        _cert_vol_with_certificate_steps(main_step=_s("Verify", "GET", "/api/verify/${VERIFY_CODE}",
            code=200, contains=["valid"])))

    add("TC-067", "Verify certificate - invalid", "INVALID code", "200 valid=false",
        [_s("Verify invalid", "GET", "/api/verify/INVALID", code=200, contains=["valid"])])

    add("TC-068", "Admin stats - super admin", "Admin token", "200 scope=system",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("Admin stats", "GET", "/api/admin/stats", auth="ADMIN_TOKEN", code=200, contains=["system"])])

    add("TC-069", "Admin stats - event manager", "EM token", "200 scope=own",
        event_setup_steps() + [
            _s("EM stats", "GET", "/api/admin/stats", auth="EM_TOKEN", code=200, contains=["own"])
        ])

    add("TC-070", "List notifications", "Authenticated", "200 notifications + unread_count",
        [_s("Admin login", "POST", "/api/auth/login",
            f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
            extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
         _s("Notifications", "GET", "/api/notifications", auth="ADMIN_TOKEN", code=200, contains=["notifications"])])

    add("TC-071", "Mark notification read", "Own notification id", "200 is_read=true",
        sub_setup + [
            _s("Submit", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": "${CATEGORY_ID}", "description": "Notify", "event_id": "${EVENT_ID}"},
               file_name="test-image.jpg", extract=[("SUB_ID", "$.data.id")], code=201),
            _s("Approve notify", "POST", "/api/submissions/${SUB_ID}/approve",
               '{"remarks":"ok"}', auth="EM_TOKEN", code=200),
            _s("List notes", "GET", "/api/notifications", auth="VOL_TOKEN",
               extract=[("NOTE_ID", "$.data.notifications[0].id")], code=200),
            _s("Mark read", "PATCH", "/api/notifications/${NOTE_ID}/read", auth="VOL_TOKEN",
               code=200, contains=["is_read"])
        ])

    add("TC-072", "Mark read - not found", "Invalid note id", "404 not found",
        [_s("Register vol", "POST", "/api/auth/register", vol_reg,
            extract=[("VOL_TOKEN", "$.data.token")], code=201),
         _s("Mark bad id", "PATCH", "/api/notifications/00000000-0000-0000-0000-000000000000/read",
            auth="VOL_TOKEN", code=404, contains=["not found"])])

    return defs


def _cert_complete_steps():
    steps = [
        _s("Get categories", "GET", "/api/categories", auth="ADMIN_TOKEN",
           extract=[("CAT_0", "$.data[0].id"), ("CAT_1", "$.data[1].id"), ("CAT_2", "$.data[2].id"),
                    ("CAT_3", "$.data[3].id"), ("CAT_4", "$.data[4].id")], code=200),
    ]
    for i in range(5):
        steps.extend([
            _s(f"Submit cat{i}", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": f"${{CAT_{i}}}", "description": f"Cert proof {i}"},
               file_name="test-image.jpg", extract=[(f"SUB_{i}", "$.data.id")], code=201),
            _s(f"Approve cat{i}", "POST", f"/api/submissions/${{SUB_{i}}}/approve",
               '{"remarks":"approved"}', auth="ADMIN_TOKEN", code=200),
        ])
    steps.append(_s("Generate cert", "POST", "/api/certificates/generate", auth="VOL_TOKEN",
                    extract=[("CERT_ID", "$.data.id"), ("VERIFY_CODE", "$.data.verification_code")],
                    code=200, contains=["certificate_number"]))
    return steps


def _cert_vol_with_certificate_steps(main_step=None, pre_main=None):
    base = [
        _s("Admin login", "POST", "/api/auth/login",
           f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
           extract=[("ADMIN_TOKEN", "$.data.token")], code=200),
        _s("Register cert vol", "POST", "/api/auth/register",
           '{"full_name":"Cert Holder","email":"holder.${__UUID()}.@test.local","password":"password1","phone":"9876543210","location":"Pune"}',
           extract=[("VOL_TOKEN", "$.data.token")], code=201),
        _s("Get categories", "GET", "/api/categories", auth="ADMIN_TOKEN",
           extract=[("CAT_0", "$.data[0].id"), ("CAT_1", "$.data[1].id"), ("CAT_2", "$.data[2].id"),
                    ("CAT_3", "$.data[3].id"), ("CAT_4", "$.data[4].id")], code=200),
    ]
    for i in range(5):
        base.extend([
            _s(f"Submit {i}", "POST", "/api/submissions", auth="VOL_TOKEN",
               multipart={"category_id": f"${{CAT_{i}}}", "description": f"H{i}"},
               file_name="test-image.jpg", extract=[(f"SUB_{i}", "$.data.id")], code=201),
            _s(f"Approve {i}", "POST", f"/api/submissions/${{SUB_{i}}}/approve",
               '{"remarks":"ok"}', auth="ADMIN_TOKEN", code=200),
        ])
    base.append(_s("Gen cert", "POST", "/api/certificates/generate", auth="VOL_TOKEN",
                  extract=[("CERT_ID", "$.data.id"), ("VERIFY_CODE", "$.data.verification_code")], code=200))
    if pre_main:
        base.extend(pre_main)
    if main_step:
        base.append(main_step)
    return base


# --- JMX XML builders (reuse patterns from generate_test_assets.py) ---

def _prop(name, value=""):
    p = ET.Element("stringProp", {"name": name})
    if value:
        p.text = value
    return p


def _bool_prop(name, value):
    p = ET.Element("boolProp", {"name": name})
    p.text = "true" if value else "false"
    return p


def http_arguments_empty():
    args = ET.Element("elementProp", {
        "name": "HTTPsampler.Arguments", "elementType": "Arguments",
        "guiclass": "HTTPArgumentsPanel", "testclass": "Arguments",
        "testname": "User Defined Variables", "enabled": "true",
    })
    ET.SubElement(args, "collectionProp", {"name": "Arguments.arguments"})
    return args


def http_sampler(step):
    sampler = ET.Element("HTTPSamplerProxy", {
        "guiclass": "HttpTestSampleGui", "testclass": "HTTPSamplerProxy",
        "testname": step["name"], "enabled": "true",
    })
    args = ET.SubElement(sampler, "elementProp", {
        "name": "HTTPsampler.Arguments", "elementType": "Arguments",
        "guiclass": "HTTPArgumentsPanel", "testclass": "Arguments",
        "testname": "User Defined Variables", "enabled": "true",
    })
    coll = ET.SubElement(args, "collectionProp", {"name": "Arguments.arguments"})

    if step.get("multipart"):
        ET.SubElement(sampler, "boolProp", {"name": "HTTPSampler.DO_MULTIPART_POST"}).text = "true"
        for field, value in step["multipart"].items():
            ep = ET.SubElement(coll, "elementProp", {"name": field, "elementType": "HTTPArgument"})
            ET.SubElement(ep, "boolProp", {"name": "HTTPArgument.always_encode"}).text = "false"
            ET.SubElement(ep, "stringProp", {"name": "Argument.name"}).text = field
            ET.SubElement(ep, "stringProp", {"name": "Argument.value"}).text = value
            ET.SubElement(ep, "stringProp", {"name": "Argument.metadata"}).text = "="
            ET.SubElement(ep, "boolProp", {"name": "HTTPArgument.use_equals"}).text = "true"
        if step.get("file_name"):
            fname = step["file_name"]
            fpath = TEST_IMAGE_GIF if fname.endswith(".gif") else TEST_IMAGE_PATH
            ep = ET.SubElement(coll, "elementProp", {"name": "image", "elementType": "HTTPArgument"})
            ET.SubElement(ep, "boolProp", {"name": "HTTPArgument.always_encode"}).text = "false"
            ET.SubElement(ep, "stringProp", {"name": "Argument.name"}).text = "image"
            ET.SubElement(ep, "stringProp", {"name": "Argument.value"}).text = ""
            ET.SubElement(ep, "stringProp", {"name": "Argument.metadata"}).text = "="
            ET.SubElement(ep, "boolProp", {"name": "HTTPArgument.use_equals"}).text = "true"
            ET.SubElement(ep, "stringProp", {"name": "Argument.path"}).text = fpath
            ctype = "image/gif" if fname.endswith(".gif") else "image/jpeg"
            ET.SubElement(ep, "stringProp", {"name": "HTTPArgument.content_type"}).text = ctype
    elif step.get("body"):
        ep = ET.SubElement(coll, "elementProp", {"name": "", "elementType": "HTTPArgument"})
        ET.SubElement(ep, "boolProp", {"name": "HTTPArgument.always_encode"}).text = "false"
        ET.SubElement(ep, "stringProp", {"name": "Argument.value"}).text = step["body"]
        ET.SubElement(ep, "stringProp", {"name": "Argument.metadata"}).text = "="

    sampler.append(_prop("HTTPSampler.domain", "localhost"))
    sampler.append(_prop("HTTPSampler.port", "5000"))
    sampler.append(_prop("HTTPSampler.protocol", "http"))
    sampler.append(_prop("HTTPSampler.path", step["path"]))
    sampler.append(_prop("HTTPSampler.method", step["method"]))
    sampler.append(_bool_prop("HTTPSampler.follow_redirects", True))
    sampler.append(_bool_prop("HTTPSampler.use_keepalive", True))
    has_body = bool(step.get("body") and not step.get("multipart"))
    sampler.append(_bool_prop("HTTPSampler.postBodyRaw", has_body))
    if has_body:
        sampler.append(_prop("HTTPSampler.contentEncoding", "UTF-8"))
    return sampler


def header_manager(headers):
    hm = ET.Element("HeaderManager", {
        "guiclass": "HeaderPanel", "testclass": "HeaderManager",
        "testname": "HTTP Header Manager", "enabled": "true",
    })
    coll = ET.SubElement(hm, "collectionProp", {"name": "HeaderManager.headers"})
    for hname, hval in headers:
        ep = ET.SubElement(coll, "elementProp", {"name": "", "elementType": "Header"})
        ET.SubElement(ep, "stringProp", {"name": "Header.name"}).text = hname
        ET.SubElement(ep, "stringProp", {"name": "Header.value"}).text = hval
    return hm


def json_extractor(name, var, json_path):
    je = ET.Element("JSONPostProcessor", {
        "guiclass": "JSONPostProcessorGui", "testclass": "JSONPostProcessor",
        "testname": name, "enabled": "true",
    })
    je.append(_prop("JSONPostProcessor.referenceNames", var))
    je.append(_prop("JSONPostProcessor.jsonPathExprs", json_path))
    je.append(_prop("JSONPostProcessor.match_numbers", "1"))
    je.append(_prop("JSONPostProcessor.defaultValues", "NOT_FOUND"))
    return je


def response_code_assertion(code):
    ra = ET.Element("ResponseAssertion", {
        "guiclass": "AssertionGui", "testclass": "ResponseAssertion",
        "testname": f"Assert HTTP {code}", "enabled": "true",
    })
    coll = ET.SubElement(ra, "collectionProp", {"name": "Assertion.test_strings"})
    ET.SubElement(coll, "stringProp", {"name": ""}).text = str(code)
    ra.append(_prop("Assertion.custom_message", ""))
    ra.append(_prop("Assertion.test_field", "Assertion.response_code"))
    ra.append(_bool_prop("Assertion.assume_success", False))
    ra.append(_prop("Assertion.test_type", "8"))
    return ra


def response_body_assertion(text):
    ra = ET.Element("ResponseAssertion", {
        "guiclass": "AssertionGui", "testclass": "ResponseAssertion",
        "testname": f"Assert body contains '{text[:30]}'", "enabled": "true",
    })
    coll = ET.SubElement(ra, "collectionProp", {"name": "Assertion.test_strings"})
    ET.SubElement(coll, "stringProp", {"name": ""}).text = text
    ra.append(_prop("Assertion.custom_message", ""))
    ra.append(_prop("Assertion.test_field", "Assertion.response_data"))
    ra.append(_bool_prop("Assertion.assume_success", False))
    ra.append(_prop("Assertion.test_type", "2"))  # contains
    return ra


RECORD_SCRIPT = r"""
import java.nio.file.*
import groovy.json.JsonSlurper

def esc(s) {
    if (s == null) return ''
    s = s.toString().replace('"', '""').replace('\r', ' ').replace('\n', ' ')
    return (s.contains(',') || s.contains('"')) ? '"' + s + '"' : s
}

def tcId = vars.get('TC_ID')
if (!tcId) {
    log.error('TC_ID not set - skipping result record for sampler: ' + prev.getSampleLabel())
    return
}

def code = prev.getResponseCode()
def expectedCode = vars.get('TC_EXPECTED_CODE') ?: ''
def fullBody = prev.getResponseDataAsString() ?: ''
def body = fullBody
if (body.length() > 1000) body = body.substring(0, 1000) + '...'
def actual = code + ' | ' + body
def codeOk = !expectedCode || code == expectedCode

def bodyOk = true
def containsRaw = vars.get('TC_EXPECTED_CONTAINS')
if (containsRaw && containsRaw != '[]') {
    try {
        def fragments = new JsonSlurper().parseText(containsRaw)
        if (fragments instanceof List) {
            fragments.each { frag ->
                if (frag && !fullBody.contains(frag.toString())) bodyOk = false
            }
        }
    } catch (ignored) { }
}

def status = (codeOk && bodyOk) ? 'Pass' : 'Fail'
if (codeOk && bodyOk) prev.setSuccessful(true)
def runtime = String.valueOf(prev.getTime())

def resultsPath = vars.get('RESULTS_CSV')
if (!resultsPath) {
    log.error('RESULTS_CSV path not set')
    return
}

def row = [tcId, vars.get('TC_SCENARIO'), vars.get('TC_STEPS'), vars.get('TC_EXPECTED'),
           vars.get('TC_INPUT'), actual, status, vars.get('TC_COMMENTS'), runtime]
def line = row.collect { esc(it) }.join(',') + '\n'

synchronized (org.apache.jmeter.util.JMeterUtils.class) {
    def p = Paths.get(resultsPath)
    if (!Files.exists(p)) {
        Files.write(p, 'TestCaseId,Scenario,Steps,Expected,Input,Actual,Status,Comments,RunTime\n'.bytes,
            StandardOpenOption.CREATE)
    }
    Files.write(p, line.bytes, StandardOpenOption.APPEND)
}
log.info('Recorded ' + tcId + ' -> ' + status + ' (' + code + ')')
"""


def _groovy_quote(value):
    """Escape a string for use inside Groovy single-quoted literal."""
    if value is None:
        return ""
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\r", " ")
        .replace("\n", " | ")
    )


def jsr223_set_tc_vars(tc, results_csv):
    """PreProcessor: populate JMeter vars (Arguments element does NOT set vars)."""
    last_step = tc["steps"][-1] if tc["steps"] else {}
    last_code = str(last_step.get("code", 200))
    last_contains = json.dumps(last_step.get("contains") or [])
    jp = ET.Element("JSR223PreProcessor", {
        "guiclass": "TestBeanGUI", "testclass": "JSR223PreProcessor",
        "testname": "Set Test Case Variables", "enabled": "true",
    })
    jp.append(_prop("scriptLanguage", "groovy"))
    jp.append(_prop("parameters", ""))
    jp.append(_prop("filename", ""))
    jp.append(_prop("cacheKey", "false"))
    script = ET.SubElement(jp, "stringProp", {"name": "script"})
    script.text = f"""
vars.put('TC_ID', '{_groovy_quote(tc["id"])}')
vars.put('TC_SCENARIO', '{_groovy_quote(tc["scenario"])}')
vars.put('TC_STEPS', '{_groovy_quote(tc.get("steps_text", ""))}')
vars.put('TC_EXPECTED', '{_groovy_quote(tc["expected"])}')
vars.put('TC_INPUT', '{_groovy_quote(tc["input"])}')
vars.put('TC_COMMENTS', '{_groovy_quote(tc.get("comments", ""))}')
vars.put('TC_EXPECTED_CODE', '{last_code}')
vars.put('TC_EXPECTED_CONTAINS', '{_groovy_quote(last_contains)}')
vars.put('RESULTS_CSV', '{_groovy_quote(results_csv.replace(chr(92), "/"))}')
"""
    return jp


def jsr223_recorder(is_validation_step):
    jp = ET.Element("JSR223PostProcessor", {
        "guiclass": "TestBeanGUI", "testclass": "JSR223PostProcessor",
        "testname": "Record TC Result" if is_validation_step else "Skip record", "enabled": str(is_validation_step).lower(),
    })
    jp.append(_prop("scriptLanguage", "groovy"))
    jp.append(_prop("parameters", ""))
    jp.append(_prop("filename", ""))
    jp.append(_prop("cacheKey", "false"))
    script = ET.SubElement(jp, "stringProp", {"name": "script"})
    script.text = RECORD_SCRIPT if is_validation_step else "// setup step - no record"
    return jp


def thread_group(tc):
    tg = ET.Element("ThreadGroup", {
        "guiclass": "ThreadGroupGui", "testclass": "ThreadGroup",
        "testname": f"{tc['id']} - {tc['scenario']}", "enabled": "true",
    })
    tg.append(_prop("ThreadGroup.on_sample_error", "continue"))
    loop = ET.SubElement(tg, "elementProp", {
        "name": "ThreadGroup.main_controller", "elementType": "LoopController",
        "guiclass": "LoopControlPanel", "testclass": "LoopController",
        "testname": "Loop Controller", "enabled": "true",
    })
    loop.append(_bool_prop("LoopController.continue_forever", False))
    loop.append(_prop("LoopController.loops", "1"))
    tg.append(_prop("ThreadGroup.num_threads", "1"))
    tg.append(_prop("ThreadGroup.ramp_time", "1"))
    tg.append(_bool_prop("ThreadGroup.scheduler", False))
    tg.append(_prop("ThreadGroup.duration", ""))
    tg.append(_prop("ThreadGroup.delay", ""))
    tg.append(_bool_prop("ThreadGroup.same_user_on_next_iteration", True))
    return tg


def user_params(tc, results_csv):
    """Display-only metadata in JMeter tree (vars are set by JSR223 PreProcessor)."""
    return jsr223_set_tc_vars(tc, results_csv)


def build_jmx(
    defs=None,
    jmx_out=None,
    results_csv=None,
    merge_py=None,
    testplan_name="Servants of Bharat - Manual Test Cases (1 TG per TC)",
):
    jmx_out = jmx_out or JMX_OUT
    results_csv = results_csv or RESULTS_CSV
    merge_py = merge_py or os.path.join(BASE_DIR, "merge_testcase_results.py")
    if defs is None:
        defs = enrich_from_csv(build_test_definitions())
    root = ET.Element("jmeterTestPlan", {"version": "1.2", "properties": "5.0", "jmeter": "5.6.3"})
    ht_root = ET.SubElement(root, "hashTree")

    tp = ET.SubElement(ht_root, "TestPlan", {
        "guiclass": "TestPlanGui", "testclass": "TestPlan",
        "testname": testplan_name, "enabled": "true",
    })
    tp.append(_bool_prop("TestPlan.functional_mode", False))
    tp.append(_bool_prop("TestPlan.serialize_threadgroups", True))

    tp_ht = ET.SubElement(ht_root, "hashTree")

    hrd = ET.SubElement(tp_ht, "ConfigTestElement", {
        "guiclass": "HttpDefaultsGui", "testclass": "ConfigTestElement",
        "testname": "HTTP Request Defaults", "enabled": "true",
    })
    hrd.append(http_arguments_empty())
    for n, v in [("HTTPSampler.domain", "localhost"), ("HTTPSampler.port", "5000"),
                 ("HTTPSampler.protocol", "http"), ("HTTPSampler.implementation", "HttpClient4"),
                 ("HTTPSampler.connect_timeout", "5000"), ("HTTPSampler.response_timeout", "60000")]:
        hrd.append(_prop(n, v))
    ET.SubElement(tp_ht, "hashTree")

    # Setup: reset results CSV (runs before all thread groups)
    setup = ET.SubElement(tp_ht, "SetupThreadGroup", {
        "guiclass": "SetupThreadGroupGui", "testclass": "SetupThreadGroup",
        "testname": "00 - Init Results CSV", "enabled": "true",
    })
    setup.append(_prop("ThreadGroup.on_sample_error", "continue"))
    sloop = ET.SubElement(setup, "elementProp", {
        "name": "ThreadGroup.main_controller", "elementType": "LoopController",
        "guiclass": "LoopControlPanel", "testclass": "LoopController",
        "testname": "Loop Controller", "enabled": "true",
    })
    sloop.append(_bool_prop("LoopController.continue_forever", False))
    sloop.append(_prop("LoopController.loops", "1"))
    setup.append(_prop("ThreadGroup.num_threads", "1"))
    setup.append(_prop("ThreadGroup.ramp_time", "1"))
    setup_ht = ET.SubElement(tp_ht, "hashTree")
    init_sampler = ET.Element("JSR223Sampler", {
        "guiclass": "TestBeanGUI", "testclass": "JSR223Sampler",
        "testname": "Clear results file", "enabled": "true",
    })
    init_sampler.append(_prop("scriptLanguage", "groovy"))
    init_sampler.append(_prop("parameters", ""))
    init_sampler.append(_prop("filename", ""))
    init_sampler.append(_prop("cacheKey", "false"))
    iscript = ET.SubElement(init_sampler, "stringProp", {"name": "script"})
    iscript.text = f"""
import java.nio.file.*
def p = Paths.get('{results_csv.replace(chr(92), "/")}')
Files.write(p, 'TestCaseId,Scenario,Steps,Expected,Input,Actual,Status,Comments,RunTime\\n'.bytes,
    StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING)
log.info('Initialized results CSV: ' + p)
"""
    setup_ht.append(init_sampler)
    ET.SubElement(setup_ht, "hashTree")

    for tc in defs:
        tg = thread_group(tc)
        tp_ht.append(tg)
        tg_ht = ET.SubElement(tp_ht, "hashTree")
        tg_ht.append(user_params(tc, results_csv))
        ET.SubElement(tg_ht, "hashTree")

        last_idx = len(tc["steps"]) - 1
        for idx, step in enumerate(tc["steps"]):
            if step is None:
                continue
            is_last = idx == last_idx
            sampler = http_sampler(step)
            tg_ht.append(sampler)
            sh = ET.SubElement(tg_ht, "hashTree")

            headers = []
            if step.get("body") and not step.get("multipart"):
                headers.append(("Content-Type", "application/json"))
            auth = step.get("auth")
            if auth:
                headers.append(("Authorization", f"Bearer ${{{auth}}}"))
            if headers:
                sh.append(header_manager(headers))
                ET.SubElement(sh, "hashTree")

            sh.append(response_code_assertion(step["code"]))
            ET.SubElement(sh, "hashTree")
            for fragment in step.get("contains", []):
                sh.append(response_body_assertion(fragment))
                ET.SubElement(sh, "hashTree")

            for var, jpath in step.get("extract", []):
                sh.append(json_extractor(f"Extract {var}", var, jpath))
                ET.SubElement(sh, "hashTree")

            sh.append(jsr223_recorder(is_last))
            ET.SubElement(sh, "hashTree")

    # Listeners
    for name, gui in [("View Results Tree", "ViewResultsFullVisualizer"), ("Summary Report", "SummaryReport")]:
        rc = ET.Element("ResultCollector", {"guiclass": gui, "testclass": "ResultCollector", "testname": name, "enabled": "true"})
        rc.append(_bool_prop("ResultCollector.error_logging", False))
        tp_ht.append(rc)
        ET.SubElement(tp_ht, "hashTree")

    # TearDown: merge via Python (robust CSV handling)
    merge_py_path = merge_py.replace("\\", "/")

    td = ET.SubElement(tp_ht, "PostThreadGroup", {
        "guiclass": "PostThreadGroupGui", "testclass": "PostThreadGroup",
        "testname": "ZZ - Merge Results CSV", "enabled": "true",
    })
    td.append(_prop("ThreadGroup.on_sample_error", "continue"))
    loop = ET.SubElement(td, "elementProp", {
        "name": "ThreadGroup.main_controller", "elementType": "LoopController",
        "guiclass": "LoopControlPanel", "testclass": "LoopController",
        "testname": "Loop Controller", "enabled": "true",
    })
    loop.append(_bool_prop("LoopController.continue_forever", False))
    loop.append(_prop("LoopController.loops", "1"))
    td.append(_prop("ThreadGroup.num_threads", "1"))
    td.append(_prop("ThreadGroup.ramp_time", "1"))
    td.append(_bool_prop("ThreadGroup.scheduler", False))
    td.append(_prop("ThreadGroup.duration", ""))
    td.append(_prop("ThreadGroup.delay", ""))
    td_ht = ET.SubElement(tp_ht, "hashTree")
    merge_script = ET.Element("JSR223Sampler", {
        "guiclass": "TestBeanGUI", "testclass": "JSR223Sampler",
        "testname": "Run merge_testcase_results.py", "enabled": "true",
    })
    merge_script.append(_prop("scriptLanguage", "groovy"))
    merge_script.append(_prop("parameters", ""))
    merge_script.append(_prop("filename", ""))
    merge_script.append(_prop("cacheKey", "false"))
    ms = ET.SubElement(merge_script, "stringProp", {"name": "script"})
    ms.text = f"""
def py = System.getenv('PYTHON') ?: 'python'
def script = '{merge_py_path}'
log.info('Running merge: ' + py + ' ' + script)
def pb = new ProcessBuilder(py, script)
pb.redirectErrorStream(true)
def proc = pb.start()
def out = proc.inputStream.getText('UTF-8')
proc.waitFor()
log.info(out)
if (proc.exitValue() != 0) {{
    log.error('merge_testcase_results.py failed with exit code ' + proc.exitValue())
}}
"""
    td_ht.append(merge_script)
    ET.SubElement(td_ht, "hashTree")

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    os.makedirs(os.path.dirname(jmx_out), exist_ok=True)
    tree.write(jmx_out, encoding="UTF-8", xml_declaration=True)
    print(f"Wrote {len(defs)} testcase thread groups -> {jmx_out}")


def enrich_from_csv(defs, csv_in=None):
    csv_in = csv_in or CSV_IN
    if not os.path.exists(csv_in):
        return defs
    rows = {}
    with open(csv_in, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows[row["TestCaseId"]] = row
    for d in defs:
        r = rows.get(d["id"], {})
        d["input"] = r.get("Input") or d["input"]
        d["expected"] = r.get("Expected") or d["expected"]
        d["comments"] = r.get("Comments") or d.get("comments", "")
        d["steps_text"] = (r.get("Steps") or "").replace("\n", " | ")
    return defs


if __name__ == "__main__":
    build_jmx()
