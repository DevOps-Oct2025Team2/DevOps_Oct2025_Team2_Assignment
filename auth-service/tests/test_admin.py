import pytest

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
    data = res.get_json()
    assert "message" in data

def test_admin_delete_user_success(client, test_user):
    # Login as admin
    login_res = client.post("/api/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create a user
    create_res = client.post(
        "/api/admin/users",
        json={
            "username": "newuser",
            "password": "newpass"
        },
        headers=headers
    )
    assert create_res.status_code == 201

    # Fetch users to get ID
    users_res = client.get("/api/admin/users", headers=headers)
    assert users_res.status_code == 200

    users = users_res.get_json()
    new_user = next(u for u in users if u["username"] == "newuser")
    user_id = new_user["id"]

    # Delete the user
    delete_res = client.delete(
        f"/api/admin/users/{user_id}",
        headers=headers
    )
    assert delete_res.status_code == 200


# AC-ADMIN-02 — Prevent Admin Account Deletion
def test_admin_cannot_delete_self(client, test_user):
    # Login as admin
    login_res = client.post("/api/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_res.get_json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Get all users (admin-only endpoint)
    users_res = client.get("/api/admin/users", headers=headers)
    assert users_res.status_code == 200

    users = users_res.get_json()

    # Find admin user's ID dynamically
    admin_user = next(u for u in users if u["username"] == "admin")
    admin_id = admin_user["id"]

    # Attempt to delete own account
    res = client.delete(
        f"/api/admin/users/{admin_id}",
        headers=headers
    )

    assert res.status_code == 403
    data = res.get_json()
    assert "message" in data

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
    data = res.get_json()
    assert "message" in data