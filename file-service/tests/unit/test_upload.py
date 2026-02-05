import pytest
from io import BytesIO
from werkzeug.datastructures import FileStorage

from models import File
from db import db
from upload import save_upload_for_user

def test_save_upload_for_user_creates_file_with_correct_owner(app, tmp_path):
    """
    AC-FILE-01
    Given an authenticated user
    When a valid file is uploaded
    Then the file is stored and associated with that user
    """

    with app.app_context():
        # -------- ARRANGE --------
        user_id = 1

        # Simulate an uploaded file (this mimics Flask request.file["file"])
        file_content = b"hello world"
        fake_file = FileStorage(
            stream=BytesIO(file_content),
            filename="a.txt",
            content_type="text/plain",
        )
        
        # temp directory for this test only
        upload_dir = tmp_path 

        # allow this file size
        max_size = 1024

        # allow file types
        allowed_types = {"text/plain"}

        # -------- ACT --------
        saved_file = save_upload_for_user(
            user_id=user_id,
            file_storage=fake_file,
            upload_dir=str(upload_dir),
            max_size=max_size,
            allowed_types=allowed_types,
        )

        # -------- ASSERT --------
        # 1. DB row created
        assert File.query.count() == 1

        db_file = File.query.first()

        # 2. Ownership enforced
        assert db_file.owner_user_id == user_id

        # 3. Metadata correct
        assert db_file.filename == "a.txt"
        assert db_file.content_type == "text/plain"
        assert db_file.size_bytes ==len(file_content)

        # 4. File path exists and is inside upload_dir
        assert db_file.storage_path is not None
        assert db_file.storage_path.startswith(str(upload_dir))

def test_upload_reject_file_over_size_limit_and_persists_nothing(app, tmp_path):
    """
    AC-FILE-02
    Given an authenticated user
    When an uploaded file exceeds size limits
    Then the upload is rejected and nothing is persisted
    """
    with app.app_context():
        # Arrange
        user_id = 1

        # Create a file that is too large
        file_content =b"x" * 20 #20 bytes
        fake_file = FileStorage(
            stream=BytesIO(file_content),
            filename="big.txt",
            content_type="text/plain",
        )

        upload_dir = tmp_path
        max_size = 10
        allowed_types = {"text/plain"}

        # Act (rejection)
        with pytest.raises(ValueError):
            save_upload_for_user(
                user_id=user_id,
                file_storage=fake_file,
                upload_dir=str(upload_dir),
                max_size=max_size,
                allowed_types=allowed_types,
            )

        # Assert
        # DB row not created
        assert File.query.count() == 0
        assert len(list(upload_dir.iterdir())) == 0 # iterdir() : give me everything inside this folder
