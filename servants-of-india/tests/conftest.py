"""Shared pytest fixtures for the Sprint 1 API test suite.

Each test run uses a throwaway SQLite database seeded with the five service
categories and one Super Admin, so tests are fully isolated and need no external
services.
"""
import os
import tempfile

import pytest

# Configure a fresh temp DB + local storage BEFORE the app is imported.
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mktemp(suffix='.db')}"
os.environ["STORAGE_BACKEND"] = "local"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-at-least-32-characters-long"

from app.app import create_app          # noqa: E402
from app.extensions import db           # noqa: E402
from app.models import ServiceCategory, User, UserRole, UserStatus  # noqa: E402
from app.utils.security import hash_password  # noqa: E402

CATEGORY_NAMES = [
    "Women's Care", "Child Welfare", "Elder Care & Orphanage",
    "Environmental Plantation", "Blood Donation",
]


@pytest.fixture()
def app():
    application = create_app()
    with application.app_context():
        db.drop_all()
        db.create_all()
        # Seed the five fixed categories.
        for name in CATEGORY_NAMES:
            db.session.add(ServiceCategory(name=name))
        # Seed the first Super Admin.
        db.session.add(User(
            full_name="Super Admin", email="admin@sob.local",
            password_hash=hash_password("Admin@12345"),
            role=UserRole.SUPER_ADMIN, status=UserStatus.ACTIVE,
            phone="0000000000", location="HQ", organization="Servants of Bharat",
        ))
        db.session.commit()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


# ------------------------------------------------------------------ helpers
@pytest.fixture()
def make_user(app):
    """Factory: create a user of a given role and return the row."""
    def _make(role=UserRole.VOLUNTEER, email=None, status=UserStatus.ACTIVE, **kwargs):
        email = email or f"{role}-{os.urandom(3).hex()}@sob.local"
        with app.app_context():
            u = User(
                full_name=kwargs.get("full_name", email.split("@")[0]),
                email=email, password_hash=hash_password("password1"),
                role=role, status=status,
                phone=kwargs.get("phone", "9999999999"),
                location=kwargs.get("location", "Pune"),
                organization=kwargs.get("organization", "Org"),
            )
            db.session.add(u)
            db.session.commit()
            return {"id": u.id, "email": u.email, "role": u.role}
    return _make


@pytest.fixture()
def token(client):
    """Return a JWT for the given email (password defaults to the seeded values)."""
    def _token(email, password=None):
        if password is None:
            password = "Admin@12345" if email == "admin@sob.local" else "password1"
        res = client.post("/api/auth/login", json={"email": email, "password": password})
        return res.get_json()["data"]["token"]
    return _token


@pytest.fixture()
def auth(token):
    """Return an Authorization header dict for the given email."""
    def _auth(email, password=None):
        return {"Authorization": f"Bearer {token(email, password)}"}
    return _auth


# ------------------------------------------------------------------ Sprint 2 helpers
@pytest.fixture()
def cat_ids(client, auth):
    """List of the five seeded service-category ids."""
    res = client.get("/api/categories", headers=auth("admin@sob.local"))
    return [c["id"] for c in res.get_json()["data"]]


@pytest.fixture()
def make_event(client, auth):
    """Factory: create an event owned by `owner_email` and return the event dict."""
    def _make(owner_email, category_id, status="completed", **over):
        body = {
            "title": over.get("title", "Service Event"),
            "description": "An event for testing.",
            "category_id": category_id,
            "venue": "Venue", "address": "Address", "city": "Pune", "state": "Maharashtra",
            "event_date": "2026-05-01", "start_time": "09:00", "end_time": "12:00",
            "capacity": 50, "status": status,
        }
        body.update(over)
        res = client.post("/api/events", headers=auth(owner_email), json=body)
        return res.get_json()["data"]
    return _make


@pytest.fixture()
def submit_proof(client, auth):
    """Factory: a volunteer submits proof (multipart). Returns the raw response."""
    import io

    def _submit(volunteer_email, category_id, event_id=None, description="Completed the service work."):
        data = {
            "category_id": category_id,
            "description": description,
            "image": (io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIFtestimage"), "proof.jpg"),
        }
        if event_id:
            data["event_id"] = event_id
        return client.post(
            "/api/submissions", headers=auth(volunteer_email),
            data=data, content_type="multipart/form-data",
        )
    return _submit
