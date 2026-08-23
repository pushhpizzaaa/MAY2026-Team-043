"""Notifications & Admin stats API tests."""
import pytest


@pytest.fixture()
def volunteer(make_user):
    return make_user(role="volunteer", email="vol@sob.local")


@pytest.fixture()
def manager(make_user):
    return make_user(role="event_manager", email="em@sob.local")


@pytest.fixture()
def approved_once(client, auth, submit_proof, make_event, volunteer, manager, cat_ids):
    """Approve one submission so the volunteer has an approval notification."""
    ev = make_event("em@sob.local", cat_ids[0], status="completed")
    s = submit_proof("vol@sob.local", cat_ids[0], event_id=ev["id"]).get_json()["data"]
    client.post(f"/api/submissions/{s['id']}/approve", headers=auth("em@sob.local"))
    return True


# ---------------------------------------------------------------- notifications
def test_list_notifications_with_unread_count(client, auth, approved_once):
    res = client.get("/api/notifications", headers=auth("vol@sob.local"))
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["unread_count"] >= 1
    assert len(data["notifications"]) >= 1


def test_mark_notification_read(client, auth, approved_once):
    data = client.get("/api/notifications", headers=auth("vol@sob.local")).get_json()["data"]
    nid = data["notifications"][0]["id"]
    res = client.patch(f"/api/notifications/{nid}/read", headers=auth("vol@sob.local"))
    assert res.status_code == 200
    assert res.get_json()["data"]["is_read"] is True


def test_cannot_read_others_notification(client, auth, make_user, approved_once):
    data = client.get("/api/notifications", headers=auth("vol@sob.local")).get_json()["data"]
    nid = data["notifications"][0]["id"]
    make_user(role="volunteer", email="vol2@sob.local")
    res = client.patch(f"/api/notifications/{nid}/read", headers=auth("vol2@sob.local"))
    assert res.status_code == 404


def test_notifications_requires_auth(client):
    res = client.get("/api/notifications")
    assert res.status_code == 401


# ---------------------------------------------------------------- admin stats
def test_admin_stats_system_scope(client, auth, make_user):
    make_user(role="volunteer")
    make_user(role="event_manager")
    res = client.get("/api/admin/stats", headers=auth("admin@sob.local"))
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["scope"] == "system"
    assert "users" in data and "submissions" in data
    assert data["users"]["total"] >= 3


def test_manager_stats_scoped_to_own_events(client, auth, submit_proof, make_event, make_user, manager, cat_ids):
    make_user(role="volunteer", email="vol@sob.local")
    # EM's own completed event with one pending submission
    ev = make_event("em@sob.local", cat_ids[0], status="completed")
    submit_proof("vol@sob.local", cat_ids[0], event_id=ev["id"])
    res = client.get("/api/admin/stats", headers=auth("em@sob.local"))
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["scope"] == "own"
    assert data["events"] == 1
    assert data["submissions"]["pending"] == 1


def test_admin_stats_forbidden_for_volunteer(client, auth, volunteer):
    res = client.get("/api/admin/stats", headers=auth("vol@sob.local"))
    assert res.status_code == 403
