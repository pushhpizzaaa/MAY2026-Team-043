"""Submissions API tests: create (multipart), my list, review queue, get one."""
import pytest


@pytest.fixture()
def volunteer(make_user):
    return make_user(role="volunteer", email="vol@sob.local")


@pytest.fixture()
def manager(make_user):
    return make_user(role="event_manager", email="em@sob.local")


# ---------------------------------------------------------------- create
def test_create_submission_success(submit_proof, make_event, volunteer, manager, cat_ids):
    ev = make_event("em@sob.local", cat_ids[0], status="completed")
    res = submit_proof("vol@sob.local", cat_ids[0], event_id=ev["id"])
    assert res.status_code == 201
    data = res.get_json()["data"]
    assert data["status"] == "pending"
    assert data["category_id"] == cat_ids[0]


def test_create_submission_requires_volunteer_role(submit_proof, make_event, manager, cat_ids):
    ev = make_event("em@sob.local", cat_ids[0])
    res = submit_proof("em@sob.local", cat_ids[0], event_id=ev["id"])  # EM cannot submit
    assert res.status_code == 403


def test_create_submission_missing_description(client, auth, volunteer, cat_ids):
    import io
    res = client.post("/api/submissions", headers=auth("vol@sob.local"), data={
        "category_id": cat_ids[0], "image": (io.BytesIO(b"x"), "p.jpg"),
    }, content_type="multipart/form-data")
    assert res.status_code == 422


def test_create_submission_missing_image(client, auth, volunteer, cat_ids):
    res = client.post("/api/submissions", headers=auth("vol@sob.local"), data={
        "category_id": cat_ids[0], "description": "no image",
    }, content_type="multipart/form-data")
    assert res.status_code == 422


def test_duplicate_pending_rejected(submit_proof, make_event, volunteer, manager, cat_ids):
    ev = make_event("em@sob.local", cat_ids[0])
    assert submit_proof("vol@sob.local", cat_ids[0], event_id=ev["id"]).status_code == 201
    # second pending submission for the same category is blocked
    res = submit_proof("vol@sob.local", cat_ids[0], event_id=ev["id"])
    assert res.status_code == 409


def test_cannot_resubmit_after_approved(submit_proof, make_event, client, auth, volunteer, manager, cat_ids):
    ev = make_event("em@sob.local", cat_ids[0])
    s = submit_proof("vol@sob.local", cat_ids[0], event_id=ev["id"]).get_json()["data"]
    client.post(f"/api/submissions/{s['id']}/approve", headers=auth("admin@sob.local"))
    # category is completed → cannot submit again
    res = submit_proof("vol@sob.local", cat_ids[0], event_id=ev["id"])
    assert res.status_code == 409


# ---------------------------------------------------------------- my list
def test_my_submissions_list(client, auth, submit_proof, make_event, volunteer, manager, cat_ids):
    ev = make_event("em@sob.local", cat_ids[0])
    submit_proof("vol@sob.local", cat_ids[0], event_id=ev["id"])
    res = client.get("/api/submissions/me", headers=auth("vol@sob.local"))
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1


# ---------------------------------------------------------------- review queue
def test_review_queue_scoped_to_owner_em(client, auth, submit_proof, make_event, make_user, volunteer, manager, cat_ids):
    # EM1 owns the event the volunteer submits to.
    ev1 = make_event("em@sob.local", cat_ids[0])
    submit_proof("vol@sob.local", cat_ids[0], event_id=ev1["id"])
    # EM2 owns nothing here.
    make_user(role="event_manager", email="em2@sob.local")
    q1 = client.get("/api/submissions?status=pending", headers=auth("em@sob.local")).get_json()["data"]
    q2 = client.get("/api/submissions?status=pending", headers=auth("em2@sob.local")).get_json()["data"]
    assert len(q1) == 1
    assert len(q2) == 0


def test_review_queue_forbidden_for_volunteer(client, auth, volunteer):
    res = client.get("/api/submissions?status=pending", headers=auth("vol@sob.local"))
    assert res.status_code == 403


# ---------------------------------------------------------------- get one
def test_get_submission_owner(client, auth, submit_proof, make_event, volunteer, manager, cat_ids):
    ev = make_event("em@sob.local", cat_ids[0])
    s = submit_proof("vol@sob.local", cat_ids[0], event_id=ev["id"]).get_json()["data"]
    res = client.get(f"/api/submissions/{s['id']}", headers=auth("vol@sob.local"))
    assert res.status_code == 200


def test_get_submission_other_volunteer_forbidden(client, auth, submit_proof, make_event, make_user, volunteer, manager, cat_ids):
    ev = make_event("em@sob.local", cat_ids[0])
    s = submit_proof("vol@sob.local", cat_ids[0], event_id=ev["id"]).get_json()["data"]
    make_user(role="volunteer", email="vol2@sob.local")
    res = client.get(f"/api/submissions/{s['id']}", headers=auth("vol2@sob.local"))
    assert res.status_code == 403
