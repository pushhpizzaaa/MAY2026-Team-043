"""Certificates API tests: generate, me, list, download, public verify."""
import pytest


@pytest.fixture()
def volunteer(make_user):
    return make_user(role="volunteer", email="vol@sob.local")


@pytest.fixture()
def manager(make_user):
    return make_user(role="event_manager", email="em@sob.local")


@pytest.fixture()
def complete_all(client, auth, submit_proof, make_event, volunteer, manager, cat_ids):
    """Drive the volunteer to complete all five categories (submit + approve each)."""
    for i, cid in enumerate(cat_ids):
        ev = make_event("em@sob.local", cid, status="completed", title=f"Event {i}")
        s = submit_proof("vol@sob.local", cid, event_id=ev["id"]).get_json()["data"]
        r = client.post(f"/api/submissions/{s['id']}/approve", headers=auth("em@sob.local"))
        assert r.status_code == 200
    return True


# ---------------------------------------------------------------- generate
def test_generate_blocked_until_all_completed(client, auth, volunteer):
    res = client.post("/api/certificates/generate", headers=auth("vol@sob.local"))
    assert res.status_code == 400  # not all 5 categories completed


def test_generate_success_after_completion(client, auth, complete_all):
    res = client.post("/api/certificates/generate", headers=auth("vol@sob.local"))
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["certificate_number"].startswith("SOB-")
    assert data["verification_code"]


def test_generate_is_idempotent(client, auth, complete_all):
    first = client.post("/api/certificates/generate", headers=auth("vol@sob.local")).get_json()["data"]
    second = client.post("/api/certificates/generate", headers=auth("vol@sob.local")).get_json()["data"]
    assert first["certificate_number"] == second["certificate_number"]


# ---------------------------------------------------------------- me / list / download
def test_get_my_certificate(client, auth, complete_all):
    client.post("/api/certificates/generate", headers=auth("vol@sob.local"))
    res = client.get("/api/certificates/me", headers=auth("vol@sob.local"))
    assert res.status_code == 200


def test_get_my_certificate_404_before_generation(client, auth, volunteer):
    res = client.get("/api/certificates/me", headers=auth("vol@sob.local"))
    assert res.status_code == 404


def test_admin_can_list_certificates(client, auth, complete_all):
    client.post("/api/certificates/generate", headers=auth("vol@sob.local"))
    res = client.get("/api/certificates", headers=auth("admin@sob.local"))
    assert res.status_code == 200
    assert len(res.get_json()["data"]) >= 1


def test_list_certificates_forbidden_for_volunteer(client, auth, volunteer):
    res = client.get("/api/certificates", headers=auth("vol@sob.local"))
    assert res.status_code == 403


def test_download_certificate(client, auth, complete_all):
    cert = client.post("/api/certificates/generate", headers=auth("vol@sob.local")).get_json()["data"]
    res = client.get(f"/api/certificates/{cert['id']}/download", headers=auth("vol@sob.local"))
    assert res.status_code == 200
    assert "download_url" in res.get_json()["data"]


# ---------------------------------------------------------------- public verify
def test_public_verify_valid(client, auth, complete_all):
    cert = client.post("/api/certificates/generate", headers=auth("vol@sob.local")).get_json()["data"]
    res = client.get(f"/api/verify/{cert['verification_code']}")  # no auth header
    assert res.status_code == 200
    body = res.get_json()["data"]
    assert body["valid"] is True
    assert body["certificate"]["certificate_number"] == cert["certificate_number"]


def test_public_verify_invalid_code(client):
    res = client.get("/api/verify/NOTAREALCODE")
    assert res.status_code == 200
    assert res.get_json()["data"]["valid"] is False
