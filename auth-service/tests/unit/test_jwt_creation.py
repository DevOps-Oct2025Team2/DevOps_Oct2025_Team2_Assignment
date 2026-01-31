import jwt
from utils.jwt_utils import generate_token, PUBLIC_KEY, ALGORITHM

def test_jwt_contains_user_and_role():
    token = generate_token(user_id=1, role="admin")

    decoded = jwt.decode(
        token,
        PUBLIC_KEY,
        algorithms=[ALGORITHM],
        options={"verify_aud": False},
    )

    assert decoded["sub"] == "1"
    assert decoded["role"] == "admin"
