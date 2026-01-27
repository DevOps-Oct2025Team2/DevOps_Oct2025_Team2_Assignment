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


# AC-LOGIN-03 — Invalid JSON Body Handling
def test_login_invalid_json_body(client):
    response = client.post(
        "/api/login",
        data="invalid-json",
        content_type="application/json"
    )

    assert response.status_code == 400

# AC-ADMIN-01 — Create User Account (Admin)
def test_admin_create_user_success(client, test_user):
    login_res = client.post("/api/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_res.get_json()["access_token"]

    res = client.post(
        "/api/admin/users",
        json={
            "username": "newuser",
            "password": "newpass"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 201

# AC-ADMIN-01 — Prevent Duplicate User Creation
def test_admin_create_user_duplicate(client, test_user):
    login_res = client.post("/api/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_res.get_json()["access_token"]

    res = client.post(
        "/api/admin/users",
        json={
            "username": "user1",
            "password": "pass"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 400

# AC-ADMIN-02 — Delete User Account (Admin)
def test_admin_delete_user_success(client, test_user):
    login_res = client.post("/api/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_res.get_json()["access_token"]

    res = client.delete(
        "/api/admin/users/2",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 200

# AC-ADMIN-02 — Prevent Admin Account Deletion
def test_admin_cannot_delete_self(client, test_user):
    login_res = client.post("/api/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_res.get_json()["access_token"]

    res = client.delete(
        "/api/admin/users/1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 403

# AC-ADMIN-01 — Non-Admin Cannot Create User
def test_non_admin_cannot_create_user(client, test_user):
    login_res = client.post("/api/login", json={
        "username": "user1",
        "password": "user123"
    })
    token = login_res.get_json()["access_token"]

    res = client.post(
        "/api/admin/users",
        json={
            "username": "hacker",
            "password": "hackpass"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 403
