"""Progress API tests."""
import pytest


@pytest.fixture()
def volunteer(make_user):
    return make_user(role="volunteer", email="vol@sob.local")


def test_progress_initially_all_not_started(client, auth, volunteer):
    res = client.get("/api/progress/me", headers=auth("vol@sob.local"))
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["total_categories"] == 5
    assert data["completed_count"] == 0
    assert data["stars"] == 0
    assert data["all_completed"] is False
    assert all(c["status"] == "not_started" for c in data["categories"])


def test_progress_requires_volunteer(client, auth):
    res = client.get("/api/progress/me", headers=auth("admin@sob.local"))
    assert res.status_code == 403


def test_progress_reflects_approval(client, auth, submit_proof, make_event, make_user, volunteer, cat_ids):
    make_user(role="event_manager", email="em@sob.local")
    ev = make_event("em@sob.local", cat_ids[1], status="completed")
    s = submit_proof("vol@sob.local", cat_ids[1], event_id=ev["id"]).get_json()["data"]
    client.post(f"/api/submissions/{s['id']}/approve", headers=auth("em@sob.local"))
    data = client.get("/api/progress/me", headers=auth("vol@sob.local")).get_json()["data"]
    assert data["completed_count"] == 1
    assert data["stars"] == 1
