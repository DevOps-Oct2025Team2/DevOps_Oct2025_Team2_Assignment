from models import File

def get_files_for_user(user_id: int):
    """
    Business logic for the dashboard.
    Given a user_id, return ONLY the files owned by that user.

    Returns:
        List[File] (SQLAlchemy model objects)
    """

    return File.query.filter_by(owner_user_id=user_id).all()