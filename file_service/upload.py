import os
import uuid
from models import File
from db import db

def save_upload_for_user(user_id, file_storage, upload_dir, max_size, allowed_types=None):
    # basic validation
    if not file_storage or not file_storage.filename:
        raise ValueError("No file provided")
    
    if allowed_types is not None and file_storage.content_type not in allowed_types:
        raise ValueError("The uploaded file does not meet the upload requirements.")

    # Read file content to determine size
    data = file_storage.stream.read()
    size = len(data)

    # Reset stream for future use
    file_storage.stream.seek(0)

    if size > max_size:
        raise ValueError("The uploaded file does not meet the upload requirements.")
    
    # ensure upload directory exists 
    os.makedirs(upload_dir, exist_ok=True)

    # generate safe storage name
    original_name = os.path.basename(file_storage.filename)  # strips any path traversal
    ext = os.path.splitext(original_name)[1]                  # keep extension like ".txt"
    # sanitize extension to avoid path separators or unusual characters
    if not ext.startswith("."):
        ext = ""
    else:
        safe_ext = "".join(c for c in ext if c.isalnum() or c in "._-")
        if not safe_ext.startswith("."):
            ext = ""
        else:
            ext = safe_ext
    stored_name = f"{uuid.uuid4().hex}{ext}"

    storage_path = os.path.join(upload_dir, stored_name)

    # normalize and ensure storage_path stays within upload_dir
    base_dir = os.path.abspath(upload_dir)
    full_storage_path = os.path.abspath(os.path.normpath(storage_path))
    if os.path.commonpath([base_dir, full_storage_path]) != base_dir:
        raise ValueError("Invalid upload path.")
    storage_path = full_storage_path

    # Save to disk
    with open(storage_path, "wb") as f:
        f.write(data)

    # Create DB record
    file = File(
        owner_user_id=user_id,
        filename=original_name,
        storage_path=storage_path,
        content_type=file_storage.content_type,
        size_bytes=size,
    )
        
    db.session.add(file)
    db.session.commit()

    return file