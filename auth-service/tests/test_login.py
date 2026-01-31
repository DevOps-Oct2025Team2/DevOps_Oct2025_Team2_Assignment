import pytest

# AC-LOGIN-01 — Successful Login (Admin)
def test_login_success_admin(client, test_user):
    response = client.post("/api/login", json={
        "username": "admin",
        "password": "admin123"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["role"] == "admin"

# AC-LOGIN-01 — Successful Login (Non-Admin User)
def test_login_success_user(client, test_user):
    response = client.post("/api/login", json={
        "username": "user1",
        "password": "user123"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["role"] == "user"

# AC-LOGIN-02 — Failed Login (Invalid Credentials)
@pytest.mark.parametrize("username,password", [
    ("admin", "wrong"),
    ("user1", "wrong"),
    ("admin1", "admin123"),
    ("user", "user123")
])
def test_login_invalid_credentials(client, username, password):
    response = client.post("/api/login", json={
        "username": username,
        "password": password
    })

    assert response.status_code == 401
    assert "message" in response.get_json()

# AC-LOGIN-03 — Input Validation (Missing Fields)
def test_login_missing_fields(client):
    response = client.post("/api/login", json={})
    assert response.status_code == 400
    assert "message" in response.get_json()

# AC-LOGIN-03 — Invalid JSON Body Handling
def test_login_invalid_json_body(client):
    response = client.post(
        "/api/login",
        data="invalid-json",
        content_type="application/json"
    )

    assert response.status_code == 400