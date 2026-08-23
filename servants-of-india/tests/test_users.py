"""Users API tests: profile, password, admin user management."""


# ---------------------------------------------------------------- /users/me
def test_get_me(client, auth):
    res = client.get("/api/users/me", headers=auth("admin@sob.local"))
    assert res.status_code == 200
    assert res.get_json()["data"]["email"] == "admin@sob.local"


def test_get_me_requires_auth(client):
    res = client.get("/api/users/me")
    assert res.status_code == 401


def test_update_me(client, auth):
    res = client.put("/api/users/me", headers=auth("admin@sob.local"),
                     json={"location": "Chennai"})
    assert res.status_code == 200
    assert res.get_json()["data"]["location"] == "Chennai"


# ---------------------------------------------------------------- password
def test_change_password_success(client, auth):
    res = client.put("/api/users/me/password", headers=auth("admin@sob.local"),
                     json={"current_password": "Admin@12345", "new_password": "NewPass@99"})
    assert res.status_code == 200


def test_change_password_wrong_current_returns_400_not_401(client, auth):
    # Must be 400 so the frontend does NOT treat it as a session expiry / logout.
    res = client.put("/api/users/me/password", headers=auth("admin@sob.local"),
                     json={"current_password": "WRONG", "new_password": "NewPass@99"})
    assert res.status_code == 400


def test_change_password_too_short(client, auth):
    res = client.put("/api/users/me/password", headers=auth("admin@sob.local"),
                     json={"current_password": "Admin@12345", "new_password": "short"})
    assert res.status_code == 422


# ---------------------------------------------------------------- list users
def test_list_users_as_admin(client, auth, make_user):
    make_user(role="volunteer")
    res = client.get("/api/users", headers=auth("admin@sob.local"))
    assert res.status_code == 200
    assert len(res.get_json()["data"]) >= 2


def test_list_users_filter_by_role(client, auth, make_user):
    make_user(role="event_manager")
    res = client.get("/api/users?role=event_manager", headers=auth("admin@sob.local"))
    assert res.status_code == 200
    assert all(u["role"] == "event_manager" for u in res.get_json()["data"])


def test_list_users_forbidden_for_volunteer(client, auth, make_user):
    make_user(role="volunteer", email="vol@x.com")
    res = client.get("/api/users", headers=auth("vol@x.com"))
    assert res.status_code == 403


# ---------------------------------------------------------------- create user
def test_create_event_manager(client, auth):
    res = client.post("/api/users", headers=auth("admin@sob.local"), json={
        "full_name": "Rohit", "email": "rohit@x.com", "password": "password1",
        "role": "event_manager", "organization": "Trust", "phone": "9", "location": "Pune",
    })
    assert res.status_code == 201
    assert res.get_json()["data"]["role"] == "event_manager"


def test_create_event_manager_missing_org(client, auth):
    res = client.post("/api/users", headers=auth("admin@sob.local"), json={
        "full_name": "Rohit", "email": "rohit2@x.com", "password": "password1",
        "role": "event_manager", "phone": "9", "location": "Pune",
    })
    assert res.status_code == 422


def test_create_user_forbidden_for_volunteer(client, auth, make_user):
    make_user(role="volunteer", email="vol2@x.com")
    res = client.post("/api/users", headers=auth("vol2@x.com"), json={
        "full_name": "X", "email": "y@x.com", "password": "password1", "role": "super_admin",
    })
    assert res.status_code == 403


# ---------------------------------------------------------------- change status
def test_change_status_block(client, auth, make_user):
    u = make_user(role="volunteer")
    res = client.patch(f"/api/users/{u['id']}/status", headers=auth("admin@sob.local"),
                       json={"status": "blocked"})
    assert res.status_code == 200
    assert res.get_json()["data"]["status"] == "blocked"


def test_change_own_status_rejected(client, auth):
    me = client.get("/api/users/me", headers=auth("admin@sob.local")).get_json()["data"]
    res = client.patch(f"/api/users/{me['id']}/status", headers=auth("admin@sob.local"),
                       json={"status": "blocked"})
    assert res.status_code == 400


def test_change_status_invalid_value(client, auth, make_user):
    u = make_user(role="volunteer")
    res = client.patch(f"/api/users/{u['id']}/status", headers=auth("admin@sob.local"),
                       json={"status": "banana"})
    assert res.status_code == 422
