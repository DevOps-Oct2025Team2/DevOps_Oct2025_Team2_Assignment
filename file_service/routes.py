from flask import Blueprint, request, jsonify
from .models import File
from .dashboard import get_files_for_user


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