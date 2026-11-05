"""Unit tests for password hashing and JWT access-token creation."""

from jose import jwt

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_does_not_store_plaintext():
    password = "DevFlow-test-password-2026"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash)


def test_verify_password_rejects_incorrect_password():
    password_hash = hash_password("correct-test-password")

    assert not verify_password("incorrect-test-password", password_hash)


def test_access_token_contains_subject_and_expiration():
    settings = get_settings()
    subject = "test-user-123"

    token = create_access_token(subject)
    claims = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )

    assert claims["sub"] == subject
    assert isinstance(claims["exp"], int)
