from dashboard import get_files_for_user
from models import File
from db import db

def test_returns_only_files_owned_by_user(app):
    with app.app_context():
        db.session.add_all([
            File(owner_user_id=1, filename="a.txt", storage_path="/files/a.txt", content_type="text/plain", size_bytes=100),
            File(owner_user_id=2, filename="b.txt", storage_path="/files/b.txt", content_type="text/plain", size_bytes=200),
        ])
        db.session.commit()

        result = get_files_for_user(1)

        assert len(result) == 1
        assert result[0].owner_user_id == 1
        assert result[0].filename == "a.txt"
