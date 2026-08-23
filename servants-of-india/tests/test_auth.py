"""Auth API tests: register, login, logout."""


def _valid_registration(**over):
    body = {
        "full_name": "Ananya Sharma", "email": "ananya@example.com",
        "password": "password1", "phone": "9876543210", "location": "Pune",
    }
    body.update(over)
    return body


# ---------------------------------------------------------------- register
def test_register_success(client):
    res = client.post("/api/auth/register", json=_valid_registration())
    assert res.status_code == 201
    data = res.get_json()["data"]
    assert data["user"]["role"] == "volunteer"
    assert data["user"]["email"] == "ananya@example.com"
    assert data["token"]


def test_register_missing_phone_and_location(client):
    res = client.post("/api/auth/register", json={
        "full_name": "X", "email": "x@example.com", "password": "password1",
    })
    assert res.status_code == 422
    assert "phone" in res.get_json()["error"].lower()


def test_register_short_password(client):
    res = client.post("/api/auth/register", json=_valid_registration(password="short"))
    assert res.status_code == 422


def test_register_invalid_email(client):
    res = client.post("/api/auth/register", json=_valid_registration(email="not-an-email"))
    assert res.status_code == 422


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json=_valid_registration())
    res = client.post("/api/auth/register", json=_valid_registration())
    assert res.status_code == 409


# ---------------------------------------------------------------- login
def test_login_success(client):
    res = client.post("/api/auth/login", json={"email": "admin@sob.local", "password": "Admin@12345"})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["user"]["role"] == "super_admin"
    assert data["token"]


def test_login_wrong_password(client):
    res = client.post("/api/auth/login", json={"email": "admin@sob.local", "password": "wrong"})
    assert res.status_code == 401


def test_login_unknown_email(client):
    res = client.post("/api/auth/login", json={"email": "nobody@x.com", "password": "password1"})
    assert res.status_code == 401


def test_login_blocked_account(client, make_user):
    from app.models import UserStatus
    make_user(role="volunteer", email="blocked@x.com", status=UserStatus.BLOCKED)
    res = client.post("/api/auth/login", json={"email": "blocked@x.com", "password": "password1"})
    assert res.status_code == 403


# ---------------------------------------------------------------- logout
def test_logout(client):
    res = client.post("/api/auth/logout")
    assert res.status_code == 200
    assert res.get_json()["success"] is True
