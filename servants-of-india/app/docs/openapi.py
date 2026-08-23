"""OpenAPI 3.0 specification for the Servants of Bharat API.

The spec is authored as a single Python dict and served through Flasgger's bundled
Swagger UI (offline-capable). Interactive docs are available at ``/api/docs`` and the
raw JSON at ``/api/openapi.json``.
"""
from flasgger import Swagger


# --- Reusable component schemas -------------------------------------------------
_SCHEMAS = {
    "Error": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "example": False},
            "error": {"type": "string", "example": "Forbidden: insufficient role"},
        },
    },
    "AuthResponse": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "user": {"$ref": "#/components/schemas/User"},
                },
            },
        },
    },
    "User": {
        "type": "object",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "full_name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "phone": {"type": "string", "nullable": True},
            "location": {"type": "string", "nullable": True},
            "organization": {"type": "string", "nullable": True},
            "role": {"type": "string", "enum": ["volunteer", "event_manager", "super_admin"]},
            "status": {"type": "string", "enum": ["active", "blocked", "deactivated"]},
            "created_at": {"type": "string", "format": "date-time"},
        },
    },
    "Event": {
        "type": "object",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "slug": {"type": "string", "example": "tree-plantation-a1b2c3d4"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "category_id": {"type": "string", "format": "uuid"},
            "category_name": {"type": "string"},
            "venue": {"type": "string"},
            "address": {"type": "string"},
            "city": {"type": "string"},
            "state": {"type": "string"},
            "event_date": {"type": "string", "format": "date"},
            "start_time": {"type": "string", "example": "09:00"},
            "end_time": {"type": "string", "example": "13:00"},
            "capacity": {"type": "integer", "nullable": True},
            "status": {"type": "string", "enum": ["upcoming", "completed", "cancelled"]},
            "created_by": {"type": "string", "format": "uuid"},
            "created_by_name": {"type": "string"},
        },
    },
    "EventInput": {
        "type": "object",
        "required": ["title", "description", "category_id", "venue", "address",
                     "city", "state", "event_date", "start_time", "end_time"],
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "category_id": {"type": "string", "format": "uuid"},
            "venue": {"type": "string"},
            "address": {"type": "string"},
            "city": {"type": "string"},
            "state": {"type": "string"},
            "event_date": {"type": "string", "format": "date"},
            "start_time": {"type": "string", "example": "09:00"},
            "end_time": {"type": "string", "example": "13:00"},
            "capacity": {"type": "integer", "nullable": True},
            "status": {"type": "string", "enum": ["upcoming", "completed", "cancelled"]},
        },
    },
    "Submission": {
        "type": "object",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "volunteer_id": {"type": "string", "format": "uuid"},
            "volunteer_name": {"type": "string"},
            "category_id": {"type": "string", "format": "uuid"},
            "category_name": {"type": "string"},
            "event_id": {"type": "string", "format": "uuid", "nullable": True},
            "event_title": {"type": "string", "nullable": True},
            "image_url": {"type": "string"},
            "description": {"type": "string"},
            "status": {"type": "string", "enum": ["pending", "approved", "rejected"]},
            "submitted_at": {"type": "string", "format": "date-time"},
        },
    },
    "Certificate": {
        "type": "object",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "volunteer_id": {"type": "string", "format": "uuid"},
            "volunteer_name": {"type": "string"},
            "certificate_number": {"type": "string", "example": "SOB-2026-00001"},
            "verification_code": {"type": "string"},
            "pdf_url": {"type": "string"},
            "issued_at": {"type": "string", "format": "date-time"},
        },
    },
    "Progress": {
        "type": "object",
        "properties": {
            "categories": {"type": "array", "items": {"type": "object"}},
            "completed_count": {"type": "integer"},
            "total_categories": {"type": "integer"},
            "stars": {"type": "integer"},
            "all_completed": {"type": "boolean"},
        },
    },
    "Notification": {
        "type": "object",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "type": {"type": "string", "enum": ["approval", "rejection", "certificate", "system"]},
            "message": {"type": "string"},
            "is_read": {"type": "boolean"},
            "created_at": {"type": "string", "format": "date-time"},
        },
    },
}


def _ok(schema_ref=None):
    content = {"type": "object", "properties": {"success": {"type": "boolean"}}}
    if schema_ref:
        content["properties"]["data"] = {"$ref": f"#/components/schemas/{schema_ref}"}
    return {"description": "Success", "content": {"application/json": {"schema": content}}}


def _err(desc):
    return {"description": desc, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}


# Common reusable responses
_UNAUTH = {"401": _err("Missing/invalid token"), "403": _err("Insufficient role")}


def _tag_path(tag, summary, security=True, request=None, responses=None, params=None):
    op = {"tags": [tag], "summary": summary, "responses": responses or {"200": _ok()}}
    if security:
        op["security"] = [{"bearerAuth": []}]
    if request:
        op["requestBody"] = request
    if params:
        op["parameters"] = params
    return op


def _json_body(schema_ref, required=True):
    return {
        "required": required,
        "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{schema_ref}"}}},
    }


def build_spec() -> dict:
    """Return the complete OpenAPI 3.0 document as a dict."""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Servants of Bharat API",
            "description": (
                "REST API for the Servants of Bharat volunteer management platform. "
                "JWT bearer auth; role-based access control (volunteer / event_manager / "
                "super_admin). Obtain a token via `POST /api/auth/login`, then click "
                "**Authorize** and paste it."
            ),
            "version": "1.0.0",
        },
        "servers": [{"url": "/api", "description": "Local API base path"}],
        "components": {
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
            },
            "schemas": _SCHEMAS,
        },
        "tags": [
            {"name": "Auth", "description": "Registration & login"},
            {"name": "Users", "description": "Profile & Super Admin user management"},
            {"name": "Categories", "description": "Fixed service categories (read-only)"},
            {"name": "Events", "description": "Event CRUD with ownership checks"},
            {"name": "Submissions", "description": "Proof submissions & review queue"},
            {"name": "Reviews", "description": "Approve / reject submissions"},
            {"name": "Progress", "description": "Volunteer category progress"},
            {"name": "Certificates", "description": "Certificate generation & public verify"},
            {"name": "Notifications", "description": "In-app notifications"},
            {"name": "Admin", "description": "Dashboard statistics"},
        ],
        "paths": {
            # --- Auth ---
            "/auth/register": {
                "post": _tag_path("Auth", "Volunteer self-registration", security=False,
                                  request={"required": True, "content": {"application/json": {"schema": {
                                      "type": "object",
                                      "required": ["full_name", "email", "password", "phone", "location"],
                                      "properties": {
                                          "full_name": {"type": "string"},
                                          "email": {"type": "string"},
                                          "password": {"type": "string", "minLength": 8},
                                          "phone": {"type": "string"},
                                          "location": {"type": "string"},
                                          "organization": {"type": "string"},
                                      }}}}},
                                  responses={"201": _ok("AuthResponse"), "409": _err("Email already registered"),
                                             "422": _err("Validation error")}),
            },
            "/auth/login": {
                "post": _tag_path("Auth", "Login and receive a JWT", security=False,
                                  request={"required": True, "content": {"application/json": {"schema": {
                                      "type": "object", "required": ["email", "password"],
                                      "properties": {"email": {"type": "string"}, "password": {"type": "string"}}}}}},
                                  responses={"200": _ok("AuthResponse"), "401": _err("Invalid credentials"),
                                             "403": _err("Blocked/deactivated")}),
            },
            "/auth/logout": {
                "post": _tag_path("Auth", "Logout (client discards token)", security=False),
            },

            # --- Users ---
            "/users/me": {
                "get": _tag_path("Users", "Get current profile", responses={"200": _ok("User"), **_UNAUTH}),
                "put": _tag_path("Users", "Update own profile (email immutable)",
                                 request=_json_body("User", required=False),
                                 responses={"200": _ok("User"), **_UNAUTH}),
            },
            "/users/me/password": {
                "put": _tag_path("Users", "Change own password (stays logged in)",
                                 request={"required": True, "content": {"application/json": {"schema": {
                                     "type": "object", "required": ["current_password", "new_password"],
                                     "properties": {"current_password": {"type": "string"},
                                                    "new_password": {"type": "string", "minLength": 8}}}}}},
                                 responses={"200": _ok(), "400": _err("Current password incorrect"),
                                            "422": _err("New password too short"), **_UNAUTH}),
            },
            "/users": {
                "get": _tag_path("Users", "List all users (Super Admin)",
                                 params=[
                                     {"name": "role", "in": "query", "schema": {"type": "string"}},
                                     {"name": "status", "in": "query", "schema": {"type": "string"}},
                                 ],
                                 responses={"200": _ok(), **_UNAUTH}),
                "post": _tag_path("Users", "Create Event Manager / Super Admin (Super Admin)",
                                  request={"required": True, "content": {"application/json": {"schema": {
                                      "type": "object",
                                      "required": ["full_name", "email", "password", "role"],
                                      "properties": {
                                          "full_name": {"type": "string"},
                                          "email": {"type": "string"},
                                          "password": {"type": "string"},
                                          "role": {"type": "string", "enum": ["event_manager", "super_admin"]},
                                          "phone": {"type": "string"},
                                          "location": {"type": "string"},
                                          "organization": {"type": "string"},
                                      }}}}},
                                  responses={"201": _ok("User"), "422": _err("Validation error"), **_UNAUTH}),
            },
            "/users/{id}/status": {
                "patch": _tag_path("Users", "Change user status (Super Admin)",
                                   params=[{"name": "id", "in": "path", "required": True,
                                            "schema": {"type": "string"}}],
                                   request={"required": True, "content": {"application/json": {"schema": {
                                       "type": "object", "required": ["status"],
                                       "properties": {"status": {"type": "string",
                                                                  "enum": ["active", "blocked", "deactivated"]}}}}}},
                                   responses={"200": _ok("User"), **_UNAUTH}),
            },

            # --- Categories ---
            "/categories": {
                "get": _tag_path("Categories", "List the 5 fixed service categories"),
            },

            # --- Events ---
            "/events": {
                "get": _tag_path("Events", "List events",
                                 params=[
                                     {"name": "category", "in": "query", "schema": {"type": "string"}},
                                     {"name": "status", "in": "query", "schema": {"type": "string"}},
                                 ]),
                "post": _tag_path("Events", "Create event (Event Manager / Super Admin)",
                                  request=_json_body("EventInput"),
                                  responses={"201": _ok("Event"), "422": _err("Validation error"), **_UNAUTH}),
            },
            "/events/{identifier}": {
                "get": _tag_path("Events", "Get event by UUID or slug",
                                 params=[{"name": "identifier", "in": "path", "required": True,
                                          "schema": {"type": "string"}}],
                                 responses={"200": _ok("Event"), "404": _err("Not found")}),
                "put": _tag_path("Events", "Update event (creator or Super Admin)",
                                 params=[{"name": "identifier", "in": "path", "required": True,
                                          "schema": {"type": "string"}}],
                                 request=_json_body("EventInput", required=False),
                                 responses={"200": _ok("Event"), "403": _err("Not your event"), **_UNAUTH}),
                "delete": _tag_path("Events", "Delete event (creator or Super Admin)",
                                    params=[{"name": "identifier", "in": "path", "required": True,
                                             "schema": {"type": "string"}}],
                                    responses={"200": _ok(), "403": _err("Not your event"), **_UNAUTH}),
            },

            # --- Submissions ---
            "/submissions": {
                "get": _tag_path("Submissions", "Review queue (Event Manager sees own events only)",
                                 params=[{"name": "status", "in": "query", "schema": {"type": "string"}}]),
                "post": {
                    "tags": ["Submissions"], "summary": "Create proof submission (Volunteer, multipart)",
                    "security": [{"bearerAuth": []}],
                    "requestBody": {"required": True, "content": {"multipart/form-data": {"schema": {
                        "type": "object", "required": ["category_id", "description", "image"],
                        "properties": {
                            "category_id": {"type": "string"},
                            "description": {"type": "string"},
                            "event_id": {"type": "string"},
                            "image": {"type": "string", "format": "binary"},
                        }}}}},
                    "responses": {"201": _ok("Submission"), "409": _err("Duplicate/completed"),
                                  "413": _err("File too large"), **_UNAUTH},
                },
            },
            "/submissions/me": {
                "get": _tag_path("Submissions", "My submissions (Volunteer)"),
            },
            "/submissions/{id}": {
                "get": _tag_path("Submissions", "Get a submission",
                                 params=[{"name": "id", "in": "path", "required": True,
                                          "schema": {"type": "string"}}],
                                 responses={"200": _ok("Submission"), "404": _err("Not found"), **_UNAUTH}),
            },
            "/submissions/{id}/approve": {
                "post": _tag_path("Reviews", "Approve a submission (own event for EM)",
                                  params=[{"name": "id", "in": "path", "required": True,
                                           "schema": {"type": "string"}}],
                                  request={"content": {"application/json": {"schema": {
                                      "type": "object", "properties": {"remarks": {"type": "string"}}}}}},
                                  responses={"200": _ok("Submission"), "403": _err("Not your event"),
                                             "409": _err("Already reviewed"), **_UNAUTH}),
            },
            "/submissions/{id}/reject": {
                "post": _tag_path("Reviews", "Reject a submission (own event for EM, remarks required)",
                                  params=[{"name": "id", "in": "path", "required": True,
                                           "schema": {"type": "string"}}],
                                  request={"required": True, "content": {"application/json": {"schema": {
                                      "type": "object", "required": ["remarks"],
                                      "properties": {"remarks": {"type": "string"}}}}}},
                                  responses={"200": _ok("Submission"), "403": _err("Not your event"),
                                             "422": _err("Remarks required"), **_UNAUTH}),
            },

            # --- Progress ---
            "/progress/me": {
                "get": _tag_path("Progress", "My 5-category progress + star count",
                                 responses={"200": _ok("Progress"), **_UNAUTH}),
            },

            # --- Certificates ---
            "/certificates/generate": {
                "post": _tag_path("Certificates", "Generate my certificate (idempotent)",
                                  responses={"200": _ok("Certificate"),
                                             "400": _err("Not all categories completed"), **_UNAUTH}),
            },
            "/certificates/me": {
                "get": _tag_path("Certificates", "Get my certificate",
                                 responses={"200": _ok("Certificate"), "404": _err("No certificate yet"), **_UNAUTH}),
            },
            "/certificates": {
                "get": _tag_path("Certificates", "List all certificates (Super Admin)",
                                 responses={"200": _ok(), **_UNAUTH}),
            },
            "/certificates/{id}/download": {
                "get": _tag_path("Certificates", "Get certificate download URL",
                                 params=[{"name": "id", "in": "path", "required": True,
                                          "schema": {"type": "string"}}],
                                 responses={"200": _ok(), **_UNAUTH}),
            },
            "/verify/{verification_code}": {
                "get": _tag_path("Certificates", "PUBLIC: verify a certificate", security=False,
                                 params=[{"name": "verification_code", "in": "path", "required": True,
                                          "schema": {"type": "string"}}]),
            },

            # --- Notifications ---
            "/notifications": {
                "get": _tag_path("Notifications", "My notifications"),
            },
            "/notifications/{id}/read": {
                "patch": _tag_path("Notifications", "Mark a notification read",
                                   params=[{"name": "id", "in": "path", "required": True,
                                            "schema": {"type": "string"}}]),
            },

            # --- Admin ---
            "/admin/stats": {
                "get": _tag_path("Admin", "Dashboard statistics (scoped by role)",
                                 responses={"200": _ok(), **_UNAUTH}),
            },
        },
    }


def init_swagger(app):
    """Attach Swagger UI at /api/docs and the raw spec at /api/openapi.json."""
    config = {
        "headers": [],
        "specs": [{"endpoint": "openapi", "route": "/api/openapi.json"}],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs",
        # Tell Flasgger this is OpenAPI 3 so it does NOT also inject `swagger: "2.0"`
        # (having both makes Swagger UI refuse to render the definition).
        "openapi": "3.0.3",
    }
    return Swagger(app, template=build_spec(), config=config, merge=True)
