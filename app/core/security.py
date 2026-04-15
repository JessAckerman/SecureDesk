from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
from base64 import b64encode
from datetime import datetime, timedelta, timezone
from functools import lru_cache
import json
from pathlib import Path

from google.oauth2 import service_account

from app.core.config import CONFIG

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def sanitize_text(value: str, max_length: int = 255) -> str:
    cleaned = " ".join((value or "").strip().split())
    return cleaned[:max_length]


def sanitize_multiline(value: str, max_length: int = 2500) -> str:
    lines = [(line or "").strip() for line in (value or "").splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned[:max_length]


def validate_email(value: str) -> bool:
    return bool(EMAIL_RE.match((value or "").strip()))


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    raw_salt = salt or secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        raw_salt.encode("utf-8"),
        120_000,
    )
    return derived.hex(), raw_salt


def verify_password(password: str, expected_hash: str, salt: str) -> bool:
    calculated, _ = hash_password(password, salt=salt)
    return hmac.compare_digest(calculated, expected_hash)


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def generate_document_hash(file_path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(file_path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


@lru_cache(maxsize=1)
def _load_service_account_info() -> dict:
    with Path(CONFIG.firebase_credentials).open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def _load_signing_credentials():
    return service_account.Credentials.from_service_account_file(
        str(CONFIG.firebase_credentials)
    )


def sign_document_hash(document_hash: str) -> tuple[str, str]:
    credentials = _load_signing_credentials()
    signed = credentials.signer.sign(document_hash.encode("utf-8"))
    info = _load_service_account_info()
    return b64encode(signed).decode("utf-8"), info.get("client_email", "securedesk")


def build_lockout_expiry(minutes: int) -> datetime:
    return utc_now() + timedelta(minutes=minutes)
