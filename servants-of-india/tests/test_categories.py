"""Categories API tests (read-only list of the 5 fixed categories)."""


def test_list_categories(client, auth):
    res = client.get("/api/categories", headers=auth("admin@sob.local"))
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert len(data) == 5
    names = {c["name"] for c in data}
    assert "Blood Donation" in names


def test_list_categories_requires_auth(client):
    res = client.get("/api/categories")
    assert res.status_code == 401
