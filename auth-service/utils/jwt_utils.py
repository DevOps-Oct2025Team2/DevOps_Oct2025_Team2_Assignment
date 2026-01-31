import jwt
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PRIVATE_KEY_PATH = BASE_DIR / "ec_private.pem"
PUBLIC_KEY_PATH = BASE_DIR / "ec_public.pem"

ALGORITHM = "ES256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

with open(PRIVATE_KEY_PATH, "r") as f:
    PRIVATE_KEY = f.read()

with open(PUBLIC_KEY_PATH, "r") as f:
    PUBLIC_KEY = f.read()


def generate_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)
