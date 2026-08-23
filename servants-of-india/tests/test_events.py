"""Events API tests: list, get (by id + slug), create, update, delete + ownership."""
import pytest


def _category_id(client, auth):
    res = client.get("/api/categories", headers=auth("admin@sob.local"))
    return res.get_json()["data"][0]["id"]


def _event_body(cat_id, **over):
    body = {
        "title": "Tree Plantation Drive", "description": "Plant native saplings.",
        "category_id": cat_id, "venue": "Riverside", "address": "Near bridge",
        "city": "Pune", "state": "Maharashtra", "event_date": "2026-05-01",
        "start_time": "07:00", "end_time": "11:00", "capacity": 50, "status": "upcoming",
    }
    body.update(over)
    return body


@pytest.fixture()
def em(make_user):
    return make_user(role="event_manager", email="em@sob.local")


@pytest.fixture()
def created_event(client, auth, em):
    cat = _category_id(client, auth)
    res = client.post("/api/events", headers=auth("em@sob.local"), json=_event_body(cat))
    return res.get_json()["data"]


# ---------------------------------------------------------------- create
def test_create_event_as_manager(client, auth, em):
    cat = _category_id(client, auth)
    res = client.post("/api/events", headers=auth("em@sob.local"), json=_event_body(cat))
    assert res.status_code == 201
    assert res.get_json()["data"]["slug"].startswith("tree-plantation-drive-")


def test_create_event_forbidden_for_volunteer(client, auth, make_user):
    make_user(role="volunteer", email="vol@sob.local")
    cat = _category_id(client, auth)
    res = client.post("/api/events", headers=auth("vol@sob.local"), json=_event_body(cat))
    assert res.status_code == 403


def test_create_event_missing_title(client, auth, em):
    cat = _category_id(client, auth)
    body = _event_body(cat)
    del body["title"]
    res = client.post("/api/events", headers=auth("em@sob.local"), json=body)
    assert res.status_code == 422


def test_create_event_invalid_category(client, auth, em):
    res = client.post("/api/events", headers=auth("em@sob.local"),
                      json=_event_body("not-a-real-category"))
    assert res.status_code == 422


def test_create_event_requires_auth(client, auth, em):
    cat = _category_id(client, auth)
    res = client.post("/api/events", json=_event_body(cat))
    assert res.status_code == 401


# ---------------------------------------------------------------- list / get
def test_list_events(client, auth, created_event):
    res = client.get("/api/events", headers=auth("admin@sob.local"))
    assert res.status_code == 200
    assert len(res.get_json()["data"]) >= 1


def test_get_event_by_id(client, auth, created_event):
    res = client.get(f"/api/events/{created_event['id']}", headers=auth("admin@sob.local"))
    assert res.status_code == 200
    assert res.get_json()["data"]["id"] == created_event["id"]


def test_get_event_by_slug(client, auth, created_event):
    res = client.get(f"/api/events/{created_event['slug']}", headers=auth("admin@sob.local"))
    assert res.status_code == 200
    assert res.get_json()["data"]["id"] == created_event["id"]


def test_get_event_not_found(client, auth):
    res = client.get("/api/events/does-not-exist", headers=auth("admin@sob.local"))
    assert res.status_code == 404


# ---------------------------------------------------------------- update / delete + ownership
def test_update_event_by_owner(client, auth, created_event):
    res = client.put(f"/api/events/{created_event['id']}", headers=auth("em@sob.local"),
                     json={"status": "completed"})
    assert res.status_code == 200
    assert res.get_json()["data"]["status"] == "completed"


def test_update_event_forbidden_for_other_manager(client, auth, created_event, make_user):
    make_user(role="event_manager", email="em2@sob.local")
    res = client.put(f"/api/events/{created_event['id']}", headers=auth("em2@sob.local"),
                     json={"status": "cancelled"})
    assert res.status_code == 403


def test_admin_can_update_any_event(client, auth, created_event):
    res = client.put(f"/api/events/{created_event['id']}", headers=auth("admin@sob.local"),
                     json={"city": "Mumbai"})
    assert res.status_code == 200
    assert res.get_json()["data"]["city"] == "Mumbai"


def test_delete_event_by_owner(client, auth, created_event):
    res = client.delete(f"/api/events/{created_event['id']}", headers=auth("em@sob.local"))
    assert res.status_code == 200


def test_delete_event_forbidden_for_other_manager(client, auth, created_event, make_user):
    make_user(role="event_manager", email="em3@sob.local")
    res = client.delete(f"/api/events/{created_event['id']}", headers=auth("em3@sob.local"))
    assert res.status_code == 403
