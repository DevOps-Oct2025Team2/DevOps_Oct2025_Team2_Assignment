import os
from flask import Blueprint, request, jsonify, send_file
from models import File
from dashboard import get_files_for_user, delete_file_for_user, get_file_for_download
from flask import current_app #The Flask app that is handling this request right now
from upload import save_upload_for_user
from auth import get_authenticated_user_id

bp = Blueprint("routes", __name__)

@bp.get("/dashboard")
def dashboard():
    user_id = get_authenticated_user_id(request)

    #AC-DASH-02: unauthenticated -> 401
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # AC-DASH-03/04: server-enforced ownership filtering + empty list is OK
    files = get_files_for_user(user_id)

    return jsonify({
        "files": [
            {
                "id": f.id,
                "filename": f.filename,
                "storage_path": f.storage_path,
                "content_type": f.content_type,
                "size_bytes": f.size_bytes,
                "created_at": f.created_at.isoformat(),
            }
            for f in files
        ]
    }), 200

@bp.post("/dashboard/upload")
def upload_dashboard_file():
    # Auth check - simulate authentication using HTTP header
    user_id = get_authenticated_user_id(request)

    # If header missing / invalid, reject immediately
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Uploaded files are sent via multipart/form-data
    # Flask stores them in request.files (a dict-like object).
    # If the "file" field isn't present then reject
    if "file" not in request.files:
        return jsonify({"error" : "No file provided"}), 400
    
    # This is a Werkzeug FileStorage object (has .filename, .content_type, .stream, etc.)
    file_storage = request.files["file"]
    
    # Get CONFIG
    upload_dir = current_app.config["UPLOAD_DIR"]
    max_size = current_app.config["MAX_UPLOAD_SIZE_BYTES"]
    allowed_types = current_app.config.get("ALLOWED_CONTENT_TYPES")

    try:
         # Call Business logic
        saved = save_upload_for_user(
            user_id=user_id,
            file_storage=file_storage,
            upload_dir=upload_dir,
            max_size=max_size,
            allowed_types=allowed_types,
        )
    except ValueError as e:
        # AC-FILE-02: reject invalid upload, no persistence
        # Log internal error details server-side without exposing them to the client
        current_app.logger.warning("Upload validation failed: %s", e)
        return jsonify({"error": "Invalid upload"}), 400
    
    # Return response json
    return jsonify({
        "file" : {
            "id": saved.id,
            "filename": saved.filename,
            "storage_path": saved.storage_path,
            "content_type": saved.content_type,
            "size_bytes": saved.size_bytes,
            "created_at": saved.created_at.isoformat(),
        }
    }), 201

@bp.post("/dashboard/delete/<int:file_id>")
def delete_file(file_id: int):
    user_id = get_authenticated_user_id(request)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    ok = delete_file_for_user(user_id, file_id)
    if not ok:
        return jsonify({"error": "Not found"}), 404
    
    return jsonify({"message":"File deleted successfully"}), 200

@bp.get("/dashboard/download/<int:file_id>")
def download_file(file_id: int):
    user_id = get_authenticated_user_id(request)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    f = get_file_for_download(user_id, file_id)
    if not f:
        return jsonify({"error": "Not found"}), 404
    
    # If record exists but file missing on disk -> treat as not found
    if not f.storage_path or not os.path.exists(f.storage_path):
        return jsonify({"error": "Not found"}), 404
    
    return send_file(
        f.storage_path,
        as_attachment=True,
        download_name=f.filename,
        mimetype=f.content_type
    )