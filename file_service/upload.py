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

    # keep original filename only for metadata
    original_name = os.path.basename(file_storage.filename)

    # disk filename is server-generated ONLY (CodeQL-friendly)
    stored_name = uuid.uuid4().hex

    storage_path = os.path.join(upload_dir, stored_name)

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