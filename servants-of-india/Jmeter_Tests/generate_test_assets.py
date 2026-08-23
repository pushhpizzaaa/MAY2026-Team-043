"""Generate JMeter JMX and manual test case CSV for Servants of Bharat API."""
import csv
import html
import os
import uuid
from xml.etree import ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JMX_PATH = os.path.join(BASE_DIR, "JMeter_Scripts", "Servants_of_Bharat_API.jmx")
CSV_PATH = os.path.join(BASE_DIR, "TestCases", "API_Manual_TestCases.csv")

BASE_URL = "http://localhost:5000"
ADMIN_EMAIL = "admin@sob.local"
ADMIN_PASSWORD = "Admin@12345"

ENDPOINTS = [
    # name, method, path, auth, body, content_type, notes
    ("Health Check", "GET", "/api/health", None, None, None, "Public health probe"),
    ("Auth Register", "POST", "/api/auth/register", None,
     '{"full_name":"JMeter Volunteer","email":"jmeter.volunteer.${__time(,)}@test.local","password":"password1","phone":"9876543210","location":"Pune"}',
     "application/json", "Creates a new volunteer; uses dynamic email"),
    ("Auth Login Admin", "POST", "/api/auth/login", None,
     f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}',
     "application/json", "Super Admin login"),
    ("Auth Logout", "POST", "/api/auth/logout", "admin", None, None, "Stateless logout acknowledgement"),
    ("Get My Profile", "GET", "/api/users/me", "admin", None, None, "Authenticated profile"),
    ("Update My Profile", "PUT", "/api/users/me", "admin",
     '{"full_name":"Super Admin","location":"Chennai"}', "application/json", "Update own profile fields"),
    ("Change Password", "PUT", "/api/users/me/password", "admin",
     '{"current_password":"Admin@12345","new_password":"Admin@12345"}', "application/json", "Idempotent password change test"),
    ("List Users", "GET", "/api/users", "admin", None, None, "Super Admin only"),
    ("List Users Filter Role", "GET", "/api/users?role=event_manager", "admin", None, None, "Filter by role"),
    ("Create Event Manager", "POST", "/api/users", "admin",
     '{"full_name":"JMeter EM","email":"jmeter.em.${__time(,)}@test.local","password":"password1","role":"event_manager","organization":"SOB","phone":"9876543211","location":"Mumbai"}',
     "application/json", "Admin creates event manager"),
    ("Change User Status", "PATCH", "/api/users/${VOLUNTEER_USER_ID}/status", "admin",
     '{"status":"active"}', "application/json", "Requires VOLUNTEER_USER_ID from setup"),
    ("List Categories", "GET", "/api/categories", "admin", None, None, "Returns 5 seeded categories"),
    ("List Events", "GET", "/api/events", "admin", None, None, "List all events"),
    ("List Events Filter", "GET", "/api/events?status=upcoming", "admin", None, None, "Filter by status"),
    ("Get Event By ID", "GET", "/api/events/${EVENT_ID}", "admin", None, None, "Requires EVENT_ID from setup"),
    ("Create Event", "POST", "/api/events", "em",
     '{"title":"JMeter Tree Drive","description":"Planting saplings","category_id":"${CATEGORY_ID}","venue":"City Park","address":"Park Road","city":"Pune","state":"Maharashtra","event_date":"2026-08-15","start_time":"09:00","end_time":"12:00","capacity":50}',
     "application/json", "Event Manager or Admin"),
    ("Update Event", "PUT", "/api/events/${EVENT_ID}", "em",
     '{"status":"completed"}', "application/json", "Owner EM updates event"),
    ("Delete Event", "DELETE", "/api/events/${EVENT_ID}", "em", None, None, "Owner EM deletes event"),
    ("Create Submission", "POST", "/api/submissions", "volunteer", None, None, "Multipart: category_id, description, image"),
    ("My Submissions", "GET", "/api/submissions/me", "volunteer", None, None, "Volunteer submission history"),
    ("Review Queue", "GET", "/api/submissions", "em", None, None, "Pending submissions for manager"),
    ("Review Queue All", "GET", "/api/submissions?status=all", "admin", None, None, "All submissions admin view"),
    ("Get Submission", "GET", "/api/submissions/${SUBMISSION_ID}", "admin", None, None, "Submission detail"),
    ("Approve Submission", "POST", "/api/submissions/${SUBMISSION_ID}/approve", "em",
     '{"remarks":"Approved via JMeter"}', "application/json", "Approve pending submission"),
    ("Reject Submission", "POST", "/api/submissions/${SUBMISSION_ID}/reject", "em",
     '{"remarks":"Rejected via JMeter - resubmit with clearer photo"}', "application/json", "Reject pending submission"),
    ("My Progress", "GET", "/api/progress/me", "volunteer", None, None, "Volunteer category progress"),
    ("Generate Certificate", "POST", "/api/certificates/generate", "volunteer", None, None, "Requires all 5 categories completed"),
    ("List Certificates", "GET", "/api/certificates", "admin", None, None, "Super Admin certificate registry"),
    ("My Certificate", "GET", "/api/certificates/me", "volunteer", None, None, "Volunteer own certificate"),
    ("Download Certificate", "GET", "/api/certificates/${CERT_ID}/download", "volunteer", None, None, "Returns download URL"),
    ("Verify Certificate", "GET", "/api/verify/${VERIFY_CODE}", None, None, None, "Public verification"),
    ("Admin Stats", "GET", "/api/admin/stats", "admin", None, None, "System dashboard stats"),
    ("Admin Stats EM", "GET", "/api/admin/stats", "em", None, None, "Event Manager scoped stats"),
    ("List Notifications", "GET", "/api/notifications", "volunteer", None, None, "User notifications inbox"),
    ("Mark Notification Read", "PATCH", "/api/notifications/${NOTIFICATION_ID}/read", "volunteer", None, None, "Mark single notification read"),
]

MANUAL_CASES = [
    ("TC-001", "Health check", "1. Start backend on port 5000\n2. Send GET /api/health", "200 OK; success=true; data.status=ok", "GET /api/health (no auth)", "", "Not Run", "Smoke test", ""),
    ("TC-002", "Volunteer registration - valid", "1. POST /api/auth/register with valid body", "201 Created; token + user with role=volunteer", '{"full_name":"Test User","email":"vol@test.local","password":"password1","phone":"9876543210","location":"Pune"}', "", "Not Run", "", ""),
    ("TC-003", "Volunteer registration - missing fields", "1. POST /api/auth/register without phone/location", "422 Missing required fields", '{"full_name":"X","email":"x@test.local","password":"password1"}', "", "Not Run", "", ""),
    ("TC-004", "Volunteer registration - short password", "1. POST with password < 8 chars", "422 Password must be at least 8 characters", '{"full_name":"X","email":"x2@test.local","password":"short","phone":"1","location":"Pune"}', "", "Not Run", "", ""),
    ("TC-005", "Volunteer registration - invalid email", "1. POST with malformed email", "422 Invalid email address", '{"full_name":"X","email":"not-email","password":"password1","phone":"1","location":"Pune"}', "", "Not Run", "", ""),
    ("TC-006", "Volunteer registration - duplicate email", "1. Register same email twice", "409 Email already registered", "Same email as TC-002", "", "Not Run", "", ""),
    ("TC-007", "Login - valid admin", "1. POST /api/auth/login with seeded admin credentials", "200 OK; token + user role=super_admin", f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}', "", "Not Run", "", ""),
    ("TC-008", "Login - wrong password", "1. POST with correct email, wrong password", "401 Invalid email or password", f'{{"email":"{ADMIN_EMAIL}","password":"wrong"}}', "", "Not Run", "", ""),
    ("TC-009", "Login - unknown email", "1. POST with unregistered email", "401 Invalid email or password", '{"email":"nobody@test.local","password":"password1"}', "", "Not Run", "", ""),
    ("TC-010", "Login - blocked account", "1. Block user via admin\n2. Attempt login", "403 account blocked", "Blocked user credentials", "", "Not Run", "Requires PATCH status=blocked first", ""),
    ("TC-011", "Logout", "1. POST /api/auth/logout", "200 OK; message=Logged out", "Any (stateless JWT)", "", "Not Run", "", ""),
    ("TC-012", "Get my profile", "1. GET /api/users/me with valid Bearer token", "200 OK; own user profile", "Authorization: Bearer <token>", "", "Not Run", "", ""),
    ("TC-013", "Get my profile - no auth", "1. GET /api/users/me without token", "401 Unauthorized", "No Authorization header", "", "Not Run", "", ""),
    ("TC-014", "Update my profile", "1. PUT /api/users/me with location update", "200 OK; location updated", '{"location":"Chennai"}', "", "Not Run", "", ""),
    ("TC-015", "Update profile - empty name", "1. PUT with empty full_name", "422 full_name cannot be empty", '{"full_name":""}', "", "Not Run", "", ""),
    ("TC-016", "Change password - success", "1. PUT /api/users/me/password with correct current password", "200 Password updated", '{"current_password":"Admin@12345","new_password":"NewPass@99"}', "", "Not Run", "", ""),
    ("TC-017", "Change password - wrong current", "1. PUT with wrong current_password", "400 Current password is incorrect (NOT 401)", '{"current_password":"WRONG","new_password":"NewPass@99"}', "", "Not Run", "Must not trigger frontend logout", ""),
    ("TC-018", "Change password - short new", "1. PUT with new_password < 8", "422 New password must be at least 8 characters", '{"current_password":"Admin@12345","new_password":"short"}', "", "Not Run", "", ""),
    ("TC-019", "List users - admin", "1. GET /api/users as Super Admin", "200 OK; array of users", "Admin Bearer token", "", "Not Run", "", ""),
    ("TC-020", "List users - filter role", "1. GET /api/users?role=event_manager", "200 OK; only event_manager users", "Admin token; query role=event_manager", "", "Not Run", "", ""),
    ("TC-021", "List users - volunteer forbidden", "1. GET /api/users as volunteer", "403 Forbidden", "Volunteer Bearer token", "", "Not Run", "", ""),
    ("TC-022", "Create event manager", "1. POST /api/users as admin with EM body", "201 Created; role=event_manager", '{"full_name":"EM","email":"em@test.local","password":"password1","role":"event_manager","organization":"SOB","phone":"9876543210","location":"Pune"}', "", "Not Run", "", ""),
    ("TC-023", "Create EM - missing organization", "1. POST without organization", "422 Organization is required", "EM body without organization", "", "Not Run", "", ""),
    ("TC-024", "Create user - volunteer forbidden", "1. POST /api/users as volunteer", "403 Forbidden", "Volunteer token", "", "Not Run", "", ""),
    ("TC-025", "Change user status - block", "1. PATCH /api/users/{id}/status with blocked", "200 OK; status=blocked", '{"status":"blocked"}', "", "Not Run", "Use another user's id", ""),
    ("TC-026", "Change own status", "1. PATCH own user id", "400 You cannot change your own status", "Admin patches own id", "", "Not Run", "", ""),
    ("TC-027", "Change status - invalid", "1. PATCH with invalid status value", "422 status must be one of ...", '{"status":"banana"}', "", "Not Run", "", ""),
    ("TC-028", "List categories", "1. GET /api/categories with auth", "200 OK; exactly 5 categories", "Valid Bearer token", "", "Not Run", "", ""),
    ("TC-029", "List categories - no auth", "1. GET without token", "401 Unauthorized", "No token", "", "Not Run", "", ""),
    ("TC-030", "Create event - valid EM", "1. POST /api/events as Event Manager", "201 Created; event with slug", "Full event body + EM token", "", "Not Run", "", ""),
    ("TC-031", "Create event - volunteer forbidden", "1. POST as volunteer", "403 Forbidden", "Volunteer token + valid body", "", "Not Run", "", ""),
    ("TC-032", "Create event - missing title", "1. POST without title", "422 Missing required field", "Body missing title", "", "Not Run", "", ""),
    ("TC-033", "Create event - invalid category", "1. POST with bad category_id", "422 Invalid category_id", "Invalid UUID category_id", "", "Not Run", "", ""),
    ("TC-034", "List events", "1. GET /api/events", "200 OK; events array", "Valid token", "", "Not Run", "", ""),
    ("TC-035", "Get event by UUID", "1. GET /api/events/{uuid}", "200 OK; event object", "Existing event UUID", "", "Not Run", "", ""),
    ("TC-036", "Get event by slug", "1. GET /api/events/{title-slug-shortid}", "200 OK; same event", "Event slug", "", "Not Run", "", ""),
    ("TC-037", "Get event - not found", "1. GET unknown identifier", "404 Event not found", "does-not-exist", "", "Not Run", "", ""),
    ("TC-038", "Update event - owner", "1. PUT /api/events/{id} as owner EM", "200 OK; updated fields", '{"status":"completed"}', "", "Not Run", "", ""),
    ("TC-039", "Update event - non-owner EM", "1. PUT as different EM", "403 You can only edit your own events", "Non-owner EM token", "", "Not Run", "", ""),
    ("TC-040", "Update event - super admin", "1. PUT as Super Admin on any event", "200 OK", "Admin token", "", "Not Run", "", ""),
    ("TC-041", "Delete event - owner", "1. DELETE /api/events/{id} as owner", "200 Event deleted", "Owner EM token", "", "Not Run", "", ""),
    ("TC-042", "Delete event - non-owner", "1. DELETE as different EM", "403 You can only delete your own events", "Non-owner EM token", "", "Not Run", "", ""),
    ("TC-043", "Create submission - valid", "1. POST multipart /api/submissions as volunteer", "201 Created; pending submission", "category_id, description, image (.jpg/.png)", "", "Not Run", "Max 5 MB image", ""),
    ("TC-044", "Create submission - no image", "1. POST without image file", "422 A proof image is required", "Missing image", "", "Not Run", "", ""),
    ("TC-045", "Create submission - wrong ext", "1. POST with .gif image", "422 Image must be .jpg, .jpeg or .png", ".gif file", "", "Not Run", "", ""),
    ("TC-046", "Create submission - duplicate pending", "1. Submit same category while pending exists", "409 pending submission exists", "Same category_id", "", "Not Run", "", ""),
    ("TC-047", "Create submission - already approved", "1. Submit category already approved", "409 already completed this category", "Approved category_id", "", "Not Run", "", ""),
    ("TC-048", "My submissions", "1. GET /api/submissions/me as volunteer", "200 OK; own submissions list", "Volunteer token", "", "Not Run", "", ""),
    ("TC-049", "Review queue - EM", "1. GET /api/submissions as Event Manager", "200 OK; pending for own events", "EM token; default status=pending", "", "Not Run", "", ""),
    ("TC-050", "Review queue - admin all", "1. GET /api/submissions?status=all as admin", "200 OK; all submissions", "Admin token", "", "Not Run", "", ""),
    ("TC-051", "Get submission - owner volunteer", "1. GET /api/submissions/{id} as submitter", "200 OK; submission detail", "Volunteer token + own id", "", "Not Run", "", ""),
    ("TC-052", "Get submission - other volunteer", "1. GET another volunteer's submission", "403 Forbidden", "Different volunteer token", "", "Not Run", "", ""),
    ("TC-053", "Approve submission", "1. POST /api/submissions/{id}/approve as EM/Admin", "200 OK; status=approved; progress completed", '{"remarks":"Good work"}', "", "Not Run", "", ""),
    ("TC-054", "Approve - already reviewed", "1. Approve non-pending submission", "409 Submission already approved/rejected", "Already approved id", "", "Not Run", "", ""),
    ("TC-055", "Reject submission", "1. POST /api/submissions/{id}/reject with remarks", "200 OK; status=rejected", '{"remarks":"Photo unclear"}', "", "Not Run", "", ""),
    ("TC-056", "Reject - missing remarks", "1. POST reject without remarks", "422 rejection reason required", "{}", "", "Not Run", "", ""),
    ("TC-057", "Reject - EM wrong event", "1. EM rejects submission for another EM's event", "403 can only review own events", "Non-owner EM token", "", "Not Run", "", ""),
    ("TC-058", "My progress", "1. GET /api/progress/me as volunteer", "200 OK; 5 categories with status + stars", "Volunteer token", "", "Not Run", "", ""),
    ("TC-059", "Generate certificate - incomplete", "1. POST /api/certificates/generate before 5 approvals", "400 All 5 categories must be completed", "Volunteer with partial progress", "", "Not Run", "", ""),
    ("TC-060", "Generate certificate - success", "1. POST after all 5 categories approved", "200 OK; certificate with number and verify code", "Volunteer token", "", "Not Run", "Idempotent if already exists", ""),
    ("TC-061", "List certificates - admin", "1. GET /api/certificates as Super Admin", "200 OK; all issued certificates", "Admin token", "", "Not Run", "", ""),
    ("TC-062", "My certificate - exists", "1. GET /api/certificates/me as volunteer with cert", "200 OK; certificate object", "Volunteer with certificate", "", "Not Run", "", ""),
    ("TC-063", "My certificate - none", "1. GET /api/certificates/me before generation", "404 No certificate yet", "Volunteer without certificate", "", "Not Run", "", ""),
    ("TC-064", "Download certificate", "1. GET /api/certificates/{id}/download", "200 OK; download_url returned", "Owner volunteer or admin token", "", "Not Run", "", ""),
    ("TC-065", "Download - other volunteer", "1. Download another user's certificate", "403 Forbidden", "Different volunteer token", "", "Not Run", "", ""),
    ("TC-066", "Verify certificate - valid", "1. GET /api/verify/{code} no auth", "200 OK; valid=true + certificate summary", "Valid verification code", "", "Not Run", "Public endpoint", ""),
    ("TC-067", "Verify certificate - invalid", "1. GET /api/verify/INVALID", "200 OK; valid=false", "Unknown code", "", "Not Run", "", ""),
    ("TC-068", "Admin stats - super admin", "1. GET /api/admin/stats as admin", "200 OK; scope=system with user/event counts", "Admin token", "", "Not Run", "", ""),
    ("TC-069", "Admin stats - event manager", "1. GET /api/admin/stats as EM", "200 OK; scope=own with scoped counts", "EM token", "", "Not Run", "", ""),
    ("TC-070", "List notifications", "1. GET /api/notifications", "200 OK; notifications array + unread_count", "Authenticated token", "", "Not Run", "", ""),
    ("TC-071", "Mark notification read", "1. PATCH /api/notifications/{id}/read", "200 OK; is_read=true", "Own notification id", "", "Not Run", "", ""),
    ("TC-072", "Mark read - not found", "1. PATCH unknown or other user's notification", "404 Notification not found", "Invalid note id", "", "Not Run", "", ""),
]


def _prop(name, value):
    p = ET.Element("stringProp", {"name": name})
    p.text = value
    return p


def _bool_prop(name, value):
    p = ET.Element("boolProp", {"name": name})
    p.text = "true" if value else "false"
    return p


def http_arguments_empty():
    """Required HTTPsampler.Arguments block for ConfigTestElement and GET samplers."""
    args = ET.Element("elementProp", {
        "name": "HTTPsampler.Arguments",
        "elementType": "Arguments",
        "guiclass": "HTTPArgumentsPanel",
        "testclass": "Arguments",
        "testname": "User Defined Variables",
        "enabled": "true",
    })
    ET.SubElement(args, "collectionProp", {"name": "Arguments.arguments"})
    return args


def result_collector(name, guiclass):
    rc = ET.Element("ResultCollector", {
        "guiclass": guiclass,
        "testclass": "ResultCollector",
        "testname": name,
        "enabled": "true",
    })
    rc.append(_bool_prop("ResultCollector.error_logging", False))
    obj = ET.SubElement(rc, "objProp")
    ET.SubElement(obj, "name").text = "saveConfig"
    val = ET.SubElement(obj, "value", {"class": "SampleSaveConfiguration"})
    for tag, text in [
        ("time", "true"), ("latency", "true"), ("timestamp", "true"), ("success", "true"),
        ("label", "true"), ("code", "true"), ("message", "true"), ("threadName", "true"),
        ("dataType", "true"), ("encoding", "false"), ("assertions", "true"),
        ("subresults", "true"), ("responseData", "false"), ("samplerData", "false"),
        ("xml", "false"), ("fieldNames", "true"), ("responseHeaders", "false"),
        ("requestHeaders", "false"), ("responseDataOnError", "false"),
        ("saveAssertionResultsFailureMessage", "true"), ("assertionsResultsToSave", "0"),
        ("bytes", "true"), ("sentBytes", "true"), ("url", "true"),
        ("threadCounts", "true"), ("idleTime", "true"), ("connectTime", "true"),
    ]:
        ET.SubElement(val, tag).text = text
    rc.append(_prop("filename", ""))
    return rc


def _element_prop(name, element_type, props):
    ep = ET.Element("elementProp", {"name": name, "elementType": element_type, "guiclass": "ArgumentsPanel", "testclass": "Arguments", "testname": name, "enabled": "true"})
    coll = ET.SubElement(ep, "collectionProp", {"name": "Arguments.arguments"})
    for k, v in props:
        arg = ET.SubElement(coll, "elementProp", {"name": k, "elementType": "Argument"})
        ET.SubElement(arg, "stringProp", {"name": "Argument.name"}).text = k
        ET.SubElement(arg, "stringProp", {"name": "Argument.value"}).text = v
        ET.SubElement(arg, "stringProp", {"name": "Argument.metadata"}).text = "="
    return ep


def http_sampler(name, method, path, body=None, content_type=None, multipart=False):
    sampler = ET.Element("HTTPSamplerProxy", {
        "guiclass": "HttpTestSampleGui", "testclass": "HTTPSamplerProxy", "testname": name, "enabled": "true"
    })
    args = ET.SubElement(sampler, "elementProp", {"name": "HTTPsampler.Arguments", "elementType": "Arguments", "guiclass": "HTTPArgumentsPanel", "testclass": "Arguments", "testname": "User Defined Variables", "enabled": "true"})
    coll = ET.SubElement(args, "collectionProp", {"name": "Arguments.arguments"})

    if multipart:
        ET.SubElement(sampler, "boolProp", {"name": "HTTPSampler.DO_MULTIPART_POST"}).text = "true"
        for field, value in [("category_id", "${CATEGORY_ID}"), ("description", "JMeter proof submission test"), ("event_id", "${EVENT_ID}")]:
            ep = ET.SubElement(coll, "elementProp", {"name": field, "elementType": "HTTPArgument"})
            ET.SubElement(ep, "boolProp", {"name": "HTTPArgument.always_encode"}).text = "false"
            ET.SubElement(ep, "stringProp", {"name": "Argument.name"}).text = field
            ET.SubElement(ep, "stringProp", {"name": "Argument.value"}).text = value
            ET.SubElement(ep, "stringProp", {"name": "Argument.metadata"}).text = "="
            ET.SubElement(ep, "boolProp", {"name": "HTTPArgument.use_equals"}).text = "true"
        # file upload placeholder path - user should place test-image.jpg alongside jmx
        ep = ET.SubElement(coll, "elementProp", {"name": "image", "elementType": "HTTPArgument"})
        ET.SubElement(ep, "boolProp", {"name": "HTTPArgument.always_encode"}).text = "false"
        ET.SubElement(ep, "stringProp", {"name": "Argument.name"}).text = "image"
        ET.SubElement(ep, "stringProp", {"name": "Argument.value"}).text = "test-image.jpg"
        ET.SubElement(ep, "stringProp", {"name": "Argument.metadata"}).text = "="
        ET.SubElement(ep, "boolProp", {"name": "HTTPArgument.use_equals"}).text = "true"
        ET.SubElement(ep, "boolProp", {"name": "HTTPArgument.content_type"}).text = "false"
        ET.SubElement(ep, "stringProp", {"name": "HTTPArgument.content_type"}).text = "image/jpeg"
    elif body:
        ep = ET.SubElement(coll, "elementProp", {"name": "", "elementType": "HTTPArgument"})
        ET.SubElement(ep, "boolProp", {"name": "HTTPArgument.always_encode"}).text = "false"
        ET.SubElement(ep, "stringProp", {"name": "Argument.value"}).text = body
        ET.SubElement(ep, "stringProp", {"name": "Argument.metadata"}).text = "="

    sampler.append(_prop("HTTPSampler.domain", "localhost"))
    sampler.append(_prop("HTTPSampler.port", "5000"))
    sampler.append(_prop("HTTPSampler.protocol", "http"))
    sampler.append(_prop("HTTPSampler.path", path))
    sampler.append(_prop("HTTPSampler.method", method))
    sampler.append(_bool_prop("HTTPSampler.follow_redirects", True))
    sampler.append(_bool_prop("HTTPSampler.use_keepalive", True))
    sampler.append(_bool_prop("HTTPSampler.postBodyRaw", bool(body and not multipart)))
    if body and not multipart:
        sampler.append(_prop("HTTPSampler.contentEncoding", "UTF-8"))
    return sampler


def header_manager(headers):
    hm = ET.Element("HeaderManager", {"guiclass": "HeaderPanel", "testclass": "HeaderManager", "testname": "HTTP Header Manager", "enabled": "true"})
    coll = ET.SubElement(hm, "collectionProp", {"name": "HeaderManager.headers"})
    for hname, hval in headers:
        ep = ET.SubElement(coll, "elementProp", {"name": "", "elementType": "Header"})
        ET.SubElement(ep, "stringProp", {"name": "Header.name"}).text = hname
        ET.SubElement(ep, "stringProp", {"name": "Header.value"}).text = hval
    return hm


def json_extractor(name, var, json_path, default="NOT_FOUND"):
    je = ET.Element("JSONPostProcessor", {"guiclass": "JSONPostProcessorGui", "testclass": "JSONPostProcessor", "testname": name, "enabled": "true"})
    je.append(_prop("JSONPostProcessor.referenceNames", var))
    je.append(_prop("JSONPostProcessor.jsonPathExprs", json_path))
    je.append(_prop("JSONPostProcessor.match_numbers", "1"))
    je.append(_prop("JSONPostProcessor.defaultValues", default))
    return je


def response_assertion(name, codes):
    ra = ET.Element("ResponseAssertion", {"guiclass": "AssertionGui", "testclass": "ResponseAssertion", "testname": name, "enabled": "true"})
    coll = ET.SubElement(ra, "collectionProp", {"name": "Assertion.test_strings"})
    for code in codes:
        ET.SubElement(coll, "stringProp", {"name": ""}).text = str(code)
    ra.append(_prop("Assertion.custom_message", ""))
    ra.append(_prop("Assertion.test_field", "Assertion.response_code"))
    ra.append(_bool_prop("Assertion.assume_success", False))
    ra.append(_prop("Assertion.test_type", "8"))  # equals
    return ra


def thread_group(name, num_threads=1, loops=1, setup=False):
    tg = ET.Element("SetupThreadGroup" if setup else "ThreadGroup", {
        "guiclass": "SetupThreadGroupGui" if setup else "ThreadGroupGui",
        "testclass": "SetupThreadGroup" if setup else "ThreadGroup",
        "testname": name,
        "enabled": "true",
    })
    tg.append(_prop("ThreadGroup.on_sample_error", "continue"))
    loop = ET.SubElement(tg, "elementProp", {"name": "ThreadGroup.main_controller", "elementType": "LoopController", "guiclass": "LoopControlPanel", "testclass": "LoopController", "testname": "Loop Controller", "enabled": "true"})
    loop.append(_bool_prop("LoopController.continue_forever", False))
    loop.append(_prop("LoopController.loops", str(loops)))
    tg.append(_prop("ThreadGroup.num_threads", str(num_threads)))
    tg.append(_prop("ThreadGroup.ramp_time", "1"))
    tg.append(_bool_prop("ThreadGroup.scheduler", False))
    tg.append(_prop("ThreadGroup.duration", ""))
    tg.append(_prop("ThreadGroup.delay", ""))
    tg.append(_bool_prop("ThreadGroup.same_user_on_next_iteration", True))
    return tg


def auth_header(auth_key):
    mapping = {
        "admin": "Bearer ${ADMIN_TOKEN}",
        "em": "Bearer ${EM_TOKEN}",
        "volunteer": "Bearer ${VOLUNTEER_TOKEN}",
    }
    if not auth_key:
        return []
    return [("Authorization", mapping[auth_key])]


def build_jmx():
    root = ET.Element("jmeterTestPlan", {"version": "1.2", "properties": "5.0", "jmeter": "5.6.3"})
    ht_root = ET.SubElement(root, "hashTree")

    tp = ET.SubElement(ht_root, "TestPlan", {"guiclass": "TestPlanGui", "testclass": "TestPlan", "testname": "Servants of Bharat - Full API Test Plan", "enabled": "true"})
    tp.append(_bool_prop("TestPlan.functional_mode", False))
    tp.append(_bool_prop("TestPlan.serialize_threadgroups", False))
    ud = ET.SubElement(tp, "elementProp", {"name": "TestPlan.user_defined_variables", "elementType": "Arguments", "guiclass": "ArgumentsPanel", "testclass": "Arguments", "testname": "User Defined Variables", "enabled": "true"})
    coll = ET.SubElement(ud, "collectionProp", {"name": "Arguments.arguments"})
    for k, v in [
        ("BASE_URL", BASE_URL),
        ("ADMIN_EMAIL", ADMIN_EMAIL),
        ("ADMIN_PASSWORD", ADMIN_PASSWORD),
        ("ADMIN_TOKEN", ""),
        ("EM_TOKEN", ""),
        ("VOLUNTEER_TOKEN", ""),
        ("CATEGORY_ID", ""),
        ("EVENT_ID", ""),
        ("SUBMISSION_ID", ""),
        ("CERT_ID", ""),
        ("VERIFY_CODE", ""),
        ("NOTIFICATION_ID", ""),
        ("VOLUNTEER_USER_ID", ""),
        ("EM_EMAIL", ""),
    ]:
        arg = ET.SubElement(coll, "elementProp", {"name": k, "elementType": "Argument"})
        ET.SubElement(arg, "stringProp", {"name": "Argument.name"}).text = k
        ET.SubElement(arg, "stringProp", {"name": "Argument.value"}).text = v
        ET.SubElement(arg, "stringProp", {"name": "Argument.metadata"}).text = "="

    tp_ht = ET.SubElement(ht_root, "hashTree")

    # Config elements
    hrd = ET.SubElement(tp_ht, "ConfigTestElement", {"guiclass": "HttpDefaultsGui", "testclass": "ConfigTestElement", "testname": "HTTP Request Defaults", "enabled": "true"})
    hrd.append(http_arguments_empty())
    hrd.append(_prop("HTTPSampler.domain", "localhost"))
    hrd.append(_prop("HTTPSampler.port", "5000"))
    hrd.append(_prop("HTTPSampler.protocol", "http"))
    hrd.append(_prop("HTTPSampler.contentEncoding", "UTF-8"))
    hrd.append(_prop("HTTPSampler.path", ""))
    hrd.append(_prop("HTTPSampler.implementation", "HttpClient4"))
    hrd.append(_prop("HTTPSampler.connect_timeout", "5000"))
    hrd.append(_prop("HTTPSampler.response_timeout", "30000"))
    ET.SubElement(tp_ht, "hashTree")

    # Setup Thread Group - extract tokens and IDs
    setup = thread_group("00 - Setup (Login & Extract Variables)", setup=True)
    tp_ht.append(setup)
    setup_ht = ET.SubElement(tp_ht, "hashTree")

    setup_steps = [
        ("Admin Login", "POST", "/api/auth/login", None, f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}', "application/json", "admin", ["ADMIN_TOKEN"], "$.data.token"),
        ("List Categories (extract CATEGORY_ID)", "GET", "/api/categories", "admin", None, None, "admin", ["CATEGORY_ID"], "$.data[0].id"),
        ("Create EM User", "POST", "/api/users", "admin",
         '{"full_name":"JMeter Setup EM","email":"jmeter.setup.em.${__time(,)}@test.local","password":"password1","role":"event_manager","organization":"SOB","phone":"9876543210","location":"Pune"}',
         "application/json", "admin", ["EM_USER_ID"], "$.data.id"),
        ("EM Login", "POST", "/api/auth/login", None, '{"email":"jmeter.setup.em.${__time(,)}@test.local","password":"password1"}', "application/json", None, ["EM_TOKEN"], "$.data.token"),
        ("Register Volunteer", "POST", "/api/auth/register", None,
         '{"full_name":"JMeter Setup Volunteer","email":"jmeter.setup.vol.${__time(,)}@test.local","password":"password1","phone":"9876543210","location":"Pune"}',
         "application/json", None, ["VOLUNTEER_TOKEN", "VOLUNTEER_USER_ID"], "$.data.token"),
    ]

    # Fix EM login - need to extract email from previous step; use JSR223 or simplified flow
    # Simpler: register volunteer extracts both token and user id with two extractors on same response

    for idx, (sname, method, path, auth, body, ctype, _, vars_, jpath) in enumerate([
        ("Admin Login", "POST", "/api/auth/login", None, f'{{"email":"{ADMIN_EMAIL}","password":"{ADMIN_PASSWORD}"}}', "application/json", None, ["ADMIN_TOKEN"], "$.data.token"),
        ("List Categories", "GET", "/api/categories", "admin", None, None, "admin", ["CATEGORY_ID"], "$.data[0].id"),
        ("Register Volunteer", "POST", "/api/auth/register", None,
         '{"full_name":"JMeter Setup Volunteer","email":"jmeter.setup.vol.${__time(,)}@test.local","password":"password1","phone":"9876543210","location":"Pune"}',
         "application/json", None, ["VOLUNTEER_TOKEN"], "$.data.token"),
    ]):
        sampler = http_sampler(sname, method, path, body, ctype)
        setup_ht.append(sampler)
        sh = ET.SubElement(setup_ht, "hashTree")
        headers = [("Content-Type", "application/json")] if body else []
        headers.extend(auth_header(auth if auth != "admin" else ("admin" if idx > 0 else None)))
        if headers:
            sh.append(header_manager(headers))
            ET.SubElement(sh, "hashTree")
        sh.append(json_extractor(f"Extract {vars_[0]}", vars_[0], jpath))
        ET.SubElement(sh, "hashTree")
        if sname == "Register Volunteer":
            sh.append(json_extractor("Extract VOLUNTEER_USER_ID", "VOLUNTEER_USER_ID", "$.data.user.id"))
            ET.SubElement(sh, "hashTree")

    # Create EM via admin then login
    em_create = http_sampler("Create EM User", "POST", "/api/users",
        '{"full_name":"JMeter Setup EM","email":"jmeter.em.setup.${__time(,)}@test.local","password":"password1","role":"event_manager","organization":"SOB","phone":"9876543210","location":"Pune"}',
        "application/json")
    setup_ht.append(em_create)
    eh = ET.SubElement(setup_ht, "hashTree")
    eh.append(header_manager([("Content-Type", "application/json"), ("Authorization", "Bearer ${ADMIN_TOKEN}")]))
    ET.SubElement(eh, "hashTree")
    eh.append(json_extractor("Extract EM_EMAIL", "EM_EMAIL", "$.data.email"))
    ET.SubElement(eh, "hashTree")

    em_login = http_sampler("EM Login", "POST", "/api/auth/login",
        '{"email":"${EM_EMAIL}","password":"password1"}', "application/json")
    setup_ht.append(em_login)
    elh = ET.SubElement(setup_ht, "hashTree")
    elh.append(header_manager([("Content-Type", "application/json")]))
    ET.SubElement(elh, "hashTree")
    elh.append(json_extractor("Extract EM_TOKEN", "EM_TOKEN", "$.data.token"))
    ET.SubElement(elh, "hashTree")

    create_event = http_sampler("Create Event (Setup)", "POST", "/api/events",
        '{"title":"JMeter Setup Event","description":"Setup event for tests","category_id":"${CATEGORY_ID}","venue":"Park","address":"Road 1","city":"Pune","state":"MH","event_date":"2026-09-01","start_time":"10:00","end_time":"13:00"}',
        "application/json")
    setup_ht.append(create_event)
    ceh = ET.SubElement(setup_ht, "hashTree")
    ceh.append(header_manager([("Content-Type", "application/json"), ("Authorization", "Bearer ${EM_TOKEN}")]))
    ET.SubElement(ceh, "hashTree")
    ceh.append(json_extractor("Extract EVENT_ID", "EVENT_ID", "$.data.id"))
    ET.SubElement(ceh, "hashTree")

    # Per-endpoint thread groups
    for ep in ENDPOINTS:
        name, method, path, auth, body, ctype, notes = ep
        tg_name = f"TG - {name} ({method} {path.split('?')[0]})"
        tg = thread_group(tg_name)
        tp_ht.append(tg)
        tg_ht = ET.SubElement(tp_ht, "hashTree")

        is_multipart = name == "Create Submission"
        sampler = http_sampler(f"{method} {path}", method, path, body if not is_multipart else None, ctype, multipart=is_multipart)
        tg_ht.append(sampler)
        sh = ET.SubElement(tg_ht, "hashTree")

        headers = []
        if body and not is_multipart:
            headers.append(("Content-Type", ctype or "application/json"))
        headers.extend(auth_header(auth))
        if headers:
            sh.append(header_manager(headers))
            ET.SubElement(sh, "hashTree")

        # Expected status codes
        expected = {
            "Health Check": ["200"],
            "Auth Register": ["201"],
            "Auth Login Admin": ["200"],
            "Auth Logout": ["200"],
            "Create Event Manager": ["201"],
            "Create Event": ["201"],
            "Create Submission": ["201"],
            "Generate Certificate": ["200", "400"],
            "My Certificate": ["200", "404"],
            "Approve Submission": ["200", "404", "409"],
            "Reject Submission": ["200", "404", "409"],
            "Delete Event": ["200", "404"],
            "Change User Status": ["200", "400", "404"],
            "Mark Notification Read": ["200", "404"],
            "Download Certificate": ["200", "404"],
            "Verify Certificate": ["200"],
        }.get(name, ["200", "201", "400", "401", "403", "404", "409", "422"])

        sh.append(response_assertion("Response Code Assertion", expected))
        ET.SubElement(sh, "hashTree")

        # Extractors for downstream tests
        if name == "Auth Login Admin":
            sh.append(json_extractor("Extract ADMIN_TOKEN", "ADMIN_TOKEN", "$.data.token"))
            ET.SubElement(sh, "hashTree")
        elif name == "Auth Register":
            sh.append(json_extractor("Extract VOLUNTEER_TOKEN", "VOLUNTEER_TOKEN", "$.data.token"))
            ET.SubElement(sh, "hashTree")
        elif name == "Create Event":
            sh.append(json_extractor("Extract EVENT_ID", "EVENT_ID", "$.data.id"))
            ET.SubElement(sh, "hashTree")
        elif name == "Create Submission":
            sh.append(json_extractor("Extract SUBMISSION_ID", "SUBMISSION_ID", "$.data.id"))
            ET.SubElement(sh, "hashTree")
        elif name == "My Certificate":
            sh.append(json_extractor("Extract CERT_ID", "CERT_ID", "$.data.id"))
            sh2 = ET.SubElement(sh, "hashTree")
            sh2.append(json_extractor("Extract VERIFY_CODE", "VERIFY_CODE", "$.data.verification_code"))
            ET.SubElement(sh2, "hashTree")
        elif name == "List Notifications":
            sh.append(json_extractor("Extract NOTIFICATION_ID", "NOTIFICATION_ID", "$.data.notifications[0].id"))
            ET.SubElement(sh, "hashTree")

    # Listeners
    for lname, lgclass in [
        ("View Results Tree", "ViewResultsFullVisualizer"),
        ("Summary Report", "SummaryReport"),
    ]:
        tp_ht.append(result_collector(lname, lgclass))
        ET.SubElement(tp_ht, "hashTree")

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    os.makedirs(os.path.dirname(JMX_PATH), exist_ok=True)
    tree.write(JMX_PATH, encoding="UTF-8", xml_declaration=True)
    print(f"Wrote JMX: {JMX_PATH}")


def build_csv():
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["TestCaseId", "Scenario", "Steps", "Expected", "Input", "Actual", "Status", "Comments", "RunTime"])
        writer.writerows(MANUAL_CASES)
    print(f"Wrote CSV: {CSV_PATH} ({len(MANUAL_CASES)} cases)")


if __name__ == "__main__":
    build_jmx()
    build_csv()
