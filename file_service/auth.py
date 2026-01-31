import os
import jwt
from jwt.exceptions import PyJWTError

def get_authenticated_user_id(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None

    token = auth.split(" ", 1)[1].strip()
    if not token:
        return None

    # Match user_service behavior
    testing = os.getenv("TESTING") == "true"

    if testing:
        alg = "HS256"
        key = os.getenv("JWT_SECRET", "test-secret")
        options = {"require": ["exp"]}
    else:
        alg = "ES256"
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        PUBLIC_KEY_PATH = os.path.join(BASE_DIR, "ec_public.pem")
        try:
            with open(PUBLIC_KEY_PATH, "rb") as f:
                key = f.read()
        except FileNotFoundError:
            print("ec_public.pem not found")
            return None
        options = {"require": ["exp"]}

    try:
        payload = jwt.decode(token, key, algorithms=[alg], options=options)
    except PyJWTError as e:
        print("JWT decode failed:", e)
        return None

    user_id = payload.get("sub")
    if isinstance(user_id, int):
        return user_id
    if isinstance(user_id, str) and user_id.isdigit():
        return int(user_id)
    return None
