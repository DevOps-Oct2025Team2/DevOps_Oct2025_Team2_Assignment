import os
import jwt
from datetime import datetime, timedelta, UTC
from pathlib import Path

# ===== Config =====
ACCESS_TOKEN_EXPIRE_MINUTES = 60

IS_TEST = (
    os.getenv("TESTING") == "true"
    or os.getenv("CI") == "true"
)

BASE_DIR = Path(__file__).resolve().parent

# ===== Key + Algorithm Selection =====
if IS_TEST:
    # CI / pytest / unit tests
    ALGORITHM = "HS256"
    PRIVATE_KEY = os.getenv("JWT_SECRET", "test-secret")
    PUBLIC_KEY = PRIVATE_KEY
else:
    # Local dev / production
    ALGORITHM = "ES256"

    PRIVATE_KEY_PATH = BASE_DIR / "ec_private.pem"
    PUBLIC_KEY_PATH = BASE_DIR / "ec_public.pem"

    if not PRIVATE_KEY_PATH.exists() or not PUBLIC_KEY_PATH.exists():
        raise RuntimeError("JWT key files missing for ES256 mode")

    PRIVATE_KEY = PRIVATE_KEY_PATH.read_text()
    PUBLIC_KEY = PUBLIC_KEY_PATH.read_text()

# ===== Token Creation =====
def generate_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),   #
        "role": role,
        "exp": datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)

# ===== Token Decode =====
def decode_token(token: str) -> dict:
    return jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
