from datetime import datetime
from db import db

class File(db.Model):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    owner_user_id = db.Column(db.Integer, nullable=False)

    filename = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(500), nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    size_bytes = db.Column(db.BigInteger, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
