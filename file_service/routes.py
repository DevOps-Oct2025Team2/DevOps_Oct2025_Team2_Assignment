from flask import Blueprint, request, jsonify
from models import File
from dashboard import get_files_for_user
from flask import current_app #The Flask app that is handling this request right now
from upload import save_upload_for_user

bp = Blueprint("routes", __name__)

@bp.get("/dashboard")
def dashboard():
    user_id = request.headers.get("X-User-Id")

    #AC-DASH-02: unauthenticated -> 401
    if not user_id or not user_id.isdigit():
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = int(user_id)

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
    user_id = request.headers.get("X-User-Id")

    # If header missing / invalid, reject immediately
    if not user_id or not user_id.isdigit():
        return jsonify({"error" : "Unauthorised"}), 401
    
    # Convert to int once validated (business logic expects int)
    user_id = int(user_id)
    
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
            user_id=int(user_id),
            file_storage=file_storage,
            upload_dir=upload_dir,
            max_size=max_size,
            allowed_types=allowed_types,
        )
    except ValueError as e:
        # AC-FILE-02: reject invalid upload, no persistence
        return jsonify({"error": str(e)}), 400
    
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