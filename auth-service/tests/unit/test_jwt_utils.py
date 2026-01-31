import jwt
from utils.jwt_utils import generate_token, decode_token, ALGORITHM

def test_generate_token_contains_user_and_role():
    token = generate_token(user_id=1, role="admin")
    decoded = decode_token(token)

    assert decoded["sub"] == "1"
    assert decoded["role"] == "admin"
