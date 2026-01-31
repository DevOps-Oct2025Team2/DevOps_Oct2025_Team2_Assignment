from utils.password import hash_password, verify_password

def test_hash_password_returns_string():
    hashed = hash_password("admin123")
    assert isinstance(hashed, str)

def test_verify_password_correct():
    hashed = hash_password("admin123")
    assert verify_password("admin123", hashed) is True

def test_verify_password_wrong():
    hashed = hash_password("admin123")
    assert verify_password("wrong", hashed) is False
