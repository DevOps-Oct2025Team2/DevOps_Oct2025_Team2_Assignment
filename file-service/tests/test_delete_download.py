import os
from models import File
from db import db
from conftest import make_test_jwt

def _seed_file(app, owner_id: int, filename="a.txt", content=b"hello", content_type="text/plain"):
    """
    Helper: create a real file on disk + DB record that points to it.
    """
    upload_dir = app.config["UPLOAD_DIR"]
    os.makedirs(upload_dir, exist_ok=True)

    storage_path = os.path.join(upload_dir, filename)
    with open(storage_path, "wb") as f:
        f.write(content)

    rec = File(
        owner_user_id=owner_id,
        filename=filename,
        storage_path=storage_path,
        content_type=content_type,
        size_bytes=len(content),
    )

    db.session.add(rec)
    db.session.commit()
    return rec.id, storage_path, filename, content

# Delete
def test_delete_owned_file_success(client, app):
    with app.app_context():
        file_id, storage_path, _, _ = _seed_file(app, owner_id=1, filename="del.txt", content=b"bye")

    token = make_test_jwt(user_id=1)
    resp = client.post(f"/dashboard/delete/{file_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "deleted" in resp.get_json()["message"].lower()

    # file removed from disk + db
    with app.app_context():
        assert File.query.get(file_id) is None
    assert not os.path.exists(storage_path)

def test_delete_missing_auth_returns_401(client, app):
    with app.app_context():
        file_id, _, filename, content  = _seed_file(app, owner_id=1)

    resp = client.post(f"/dashboard/delete/{file_id}")
    assert resp.status_code == 401

def test_delete_not_owned_returns_404(client, app):
    with app.app_context():
        file_id, _, filename, content  = _seed_file(app, owner_id=1)

    token = make_test_jwt(user_id=2)
    resp = client.post(f"/dashboard/delete/{file_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404

# ---- Download route test ----
def test_download_own_file_success(client, app):
    with app.app_context():
        file_id, _, filename, content = _seed_file(app, owner_id=1, filename="dl.txt", content=b"abc123")

    token = make_test_jwt(user_id=1)
    resp = client.get(f"/dashboard/download/{file_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    # content matches
    assert resp.data == b"abc123"

    # filename is suggested for download
    cd = resp.headers.get("Content-Disposition", "")
    assert "attachment" in cd.lower()
    assert "dl.txt" in cd

def test_download_missing_auth_returns_401(client, app):
    with app.app_context():
        file_id, _, filename, content  = _seed_file(app, owner_id=1)

    resp = client.get(f"/dashboard/download/{file_id}")
    assert resp.status_code == 401

def test_download_not_owned_returns_404(client, app):
    with app.app_context():
        file_id, _, filename, content  = _seed_file(app, owner_id=2)

    token = make_test_jwt(user_id=1)
    resp = client.get(f"/dashboard/download/{file_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


def test_download_after_delete_returns_404(client, app):
    with app.app_context():
        file_id, _, filename, content  = _seed_file(app, owner_id=1,filename="gone.txt",content=b"gone")

    token = make_test_jwt(user_id=1)
    # delete
    del_resp = client.post(f"/dashboard/delete/{file_id}", headers={"Authorization": f"Bearer {token}"})
    assert del_resp.status_code == 200

    # download should fail
    dl_resp = client.get(f"/dashboard/download/{file_id}", headers={"Authorization": f"Bearer {token}"})
    assert dl_resp.status_code == 404