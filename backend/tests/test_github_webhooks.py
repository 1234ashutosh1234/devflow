import hashlib
import hmac

import pytest
from fastapi import HTTPException

from app.api.routes.github_webhooks import verify_github_signature


def make_signature(payload: bytes, secret: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


def test_valid_github_signature():
    payload = b'{"action":"opened"}'
    secret = "test-secret"

    verify_github_signature(
        payload,
        make_signature(payload, secret),
        secret,
    )


def test_invalid_github_signature():
    payload = b'{"action":"opened"}'
    secret = "test-secret"

    with pytest.raises(HTTPException) as exc_info:
        verify_github_signature(
            payload,
            "sha256=" + ("0" * 64),
            secret,
        )

    assert exc_info.value.status_code == 403


def test_missing_github_signature():
    payload = b'{"action":"opened"}'
    secret = "test-secret"

    with pytest.raises(HTTPException) as exc_info:
        verify_github_signature(
            payload,
            None,
            secret,
        )

    assert exc_info.value.status_code == 403


def test_malformed_github_signature():
    payload = b'{"action":"opened"}'
    secret = "test-secret"

    with pytest.raises(HTTPException) as exc_info:
        verify_github_signature(
            payload,
            "invalid-signature",
            secret,
        )

    assert exc_info.value.status_code == 403


def test_signature_changes_when_payload_changes():
    payload = b'{"action":"opened"}'
    modified_payload = b'{"action":"closed"}'
    secret = "test-secret"

    signature = make_signature(payload, secret)

    with pytest.raises(HTTPException) as exc_info:
        verify_github_signature(
            modified_payload,
            signature,
            secret,
        )

    assert exc_info.value.status_code == 403