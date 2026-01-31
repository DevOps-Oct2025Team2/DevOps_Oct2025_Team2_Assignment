import pytest

# AC-LOGIN-04 — Unauthorized Access (No Token)
def test_admin_access_without_token(client):
    response = client.get("/api/admin")
    assert response.status_code == 401


# AC-LOGIN-05 — Role-Based Access Enforcement
# Non-admin user must NOT access admin endpoint
def test_admin_access_denied_for_non_admin(client, test_user):
    # Login as normal user
    login_res = client.post("/api/login", json={
        "username": "user1",
        "password": "user123"
    })
    token = login_res.get_json()["access_token"]

    # Attempt admin access
    admin_res = client.get(
        "/api/admin",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert admin_res.status_code == 403
    data = admin_res.get_json()
    assert "message" in data


# AC-LOGIN-05 — Role-Based Access Enforcement
# Admin user IS allowed to access admin endpoint
def test_admin_access_allowed_for_admin(client, test_user):
    # Login as admin
    login_res = client.post("/api/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_res.get_json()["access_token"]

    # Access admin endpoint
    admin_res = client.get(
        "/api/admin",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert admin_res.status_code == 200
    data = admin_res.get_json()
    assert "message" in data


# AC-LOGIN-06 — Session / Token Security
# Token removed / invalid → access denied
def test_access_after_logout(client, test_user):
    # Login as admin
    login_res = client.post("/api/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_res.get_json()["access_token"]

    # Simulate logout by removing token (frontend behaviour)
    admin_res = client.get(
        "/api/admin",
        headers={"Authorization": "Bearer "}
    )

    assert admin_res.status_code == 401
    data = admin_res.get_json()
    assert "message" in data


# AC-LOGIN-06 — Token Structure Validation
def test_login_returns_token_and_role(client, test_user):
    response = client.post("/api/login", json={
        "username": "admin",
        "password": "admin123"
    })

    data = response.get_json()
    assert "access_token" in data
    assert "role" in data
    assert data["role"] == "admin"