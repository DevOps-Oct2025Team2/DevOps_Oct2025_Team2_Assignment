import os
from models import File
from db import db

def get_files_for_user(user_id: int):
    """
    Business logic for the dashboard.
    Given a user_id, return ONLY the files owned by that user.

    Returns:
        List[File] (SQLAlchemy model objects)
    """

    return File.query.filter_by(owner_user_id=user_id).all()


def get_owned_file_or_none(user_id: int, file_id: int):
    """
    Return the file only if it exists AND is owned by user.
    Returns None otherwise (prevents file-id probing)
    """
    return File.query.filter_by(id=file_id, owner_user_id=user_id).first()

def delete_file_for_user(user_id: int, file_id: int) -> bool:
    """
    Permanently deletes the file record + underlying stored file
    Returns True if deleted, False if not found/not owned.
    """

    f = get_owned_file_or_none(user_id, file_id)
    if not f:
        return False
    
    # Try deleting from disk first
    try:
        if f.storage_path and os.path.exists(f.storage_path):
            os.remove(f.storage_path)
    except OSError:
        # Can use RAISE if strict behaviour, for now still proceed to remove DB record
        pass

    db.session.delete(f)
    db.session.commit()
    return True

def get_file_for_download(user_id: int, file_id: int):
    """
    Returns the File object if owned; otherwise None.
    """
    return get_owned_file_or_none(user_id, file_id)

