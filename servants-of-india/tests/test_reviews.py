"""Reviews API tests: approve / reject, ownership, progress + notifications."""
import pytest


@pytest.fixture()
def volunteer(make_user):
    return make_user(role="volunteer", email="vol@sob.local")


@pytest.fixture()
def manager(make_user):
    return make_user(role="event_manager", email="em@sob.local")


@pytest.fixture()
def pending_submission(submit_proof, make_event, volunteer, manager, cat_ids):
    """A pending submission on EM 'em@sob.local's completed event."""
    ev = make_event("em@sob.local", cat_ids[0], status="completed")
    return submit_proof("vol@sob.local", cat_ids[0], event_id=ev["id"]).get_json()["data"]


# ---------------------------------------------------------------- approve
def test_owner_em_can_approve(client, auth, pending_submission):
    res = client.post(f"/api/submissions/{pending_submission['id']}/approve", headers=auth("em@sob.local"))
    assert res.status_code == 200
    assert res.get_json()["data"]["status"] == "approved"


def test_admin_can_approve_any(client, auth, pending_submission):
    res = client.post(f"/api/submissions/{pending_submission['id']}/approve", headers=auth("admin@sob.local"))
    assert res.status_code == 200


def test_other_em_cannot_approve(client, auth, make_user, pending_submission):
    make_user(role="event_manager", email="em2@sob.local")
    res = client.post(f"/api/submissions/{pending_submission['id']}/approve", headers=auth("em2@sob.local"))
    assert res.status_code == 403


def test_volunteer_cannot_approve(client, auth, pending_submission):
    res = client.post(f"/api/submissions/{pending_submission['id']}/approve", headers=auth("vol@sob.local"))
    assert res.status_code == 403


def test_double_approve_conflict(client, auth, pending_submission):
    client.post(f"/api/submissions/{pending_submission['id']}/approve", headers=auth("em@sob.local"))
    res = client.post(f"/api/submissions/{pending_submission['id']}/approve", headers=auth("em@sob.local"))
    assert res.status_code == 409


# ---------------------------------------------------------------- approval side effects
def test_approval_completes_progress(client, auth, pending_submission, cat_ids):
    client.post(f"/api/submissions/{pending_submission['id']}/approve", headers=auth("em@sob.local"))
    prog = client.get("/api/progress/me", headers=auth("vol@sob.local")).get_json()["data"]
    done = [c for c in prog["categories"] if c["category_id"] == cat_ids[0]][0]
    assert done["status"] == "completed"
    assert prog["completed_count"] == 1


def test_approval_creates_notification(client, auth, pending_submission):
    client.post(f"/api/submissions/{pending_submission['id']}/approve", headers=auth("em@sob.local"))
    notes = client.get("/api/notifications", headers=auth("vol@sob.local")).get_json()["data"]
    assert notes["unread_count"] >= 1
    assert any(n["type"] == "approval" for n in notes["notifications"])


# ---------------------------------------------------------------- reject
def test_reject_requires_remarks(client, auth, pending_submission):
    res = client.post(f"/api/submissions/{pending_submission['id']}/reject",
                      headers=auth("em@sob.local"), json={})
    assert res.status_code == 422


def test_reject_with_remarks(client, auth, pending_submission):
    res = client.post(f"/api/submissions/{pending_submission['id']}/reject",
                      headers=auth("em@sob.local"), json={"remarks": "Photo unclear"})
    assert res.status_code == 200
    assert res.get_json()["data"]["status"] == "rejected"


def test_reject_allows_resubmission(client, auth, submit_proof, pending_submission, cat_ids):
    client.post(f"/api/submissions/{pending_submission['id']}/reject",
                headers=auth("em@sob.local"), json={"remarks": "Resubmit please"})
    # after rejection the volunteer may submit again for that category
    res = submit_proof("vol@sob.local", cat_ids[0], event_id=pending_submission["event_id"])
    assert res.status_code == 201
