
from utils.password import hash_password, verify_password


def test_hash_password_returns_different_value():
    password = "secret123"
    hashed = hash_password(password)

    # Hash should not equal plain password
    assert hashed != password
    assert isinstance(hashed, str)


def test_verify_password_success():
    password = "secret123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    password = "secret123"
    hashed = hash_password(password)

    assert verify_password("wrongpassword", hashed) is False
