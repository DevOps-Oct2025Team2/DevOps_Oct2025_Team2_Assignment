import pytest
from file_service.dashboard import get_files_for_user
from file_service.models import File # Import File to insert test data
from file_service.db import db       # Import db so we can commit data
from file_service.app import app

def test_returns_only_files_owned_by_user():
    """Test get_files_for_user function"""
    with app.app_context():
        # CLEANUP - ensure deterministic test state
        File.query.delete()
        db.session.commit()

        # ARRANGE - Set up the world
        file_user_a = File(
            owner_user_id=1,
            filename="a.txt",
            storage_path="/files/a.txt",
            content_type="text/plain",
            size_bytes=100
        )

        file_user_b = File(
            owner_user_id=2,
            filename="b.txt",
            storage_path="/files/b.txt",
            content_type="text/plain",
            size_bytes=200
        )

        db.session.add(file_user_a)
        db.session.add(file_user_b)
        db.session.commit()

        # ACT - Call the function
        result = get_files_for_user(1)

        # ASSERT - Check the result
        assert len(result) == 1
        assert result[0].owner_user_id == 1
        assert result[0].filename == "a.txt"