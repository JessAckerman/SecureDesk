from __future__ import annotations

from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

from app.core.config import CONFIG


def _resolve_credentials() -> Path:
    path = CONFIG.firebase_credentials
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró la credencial de Firebase en: {path}"
        )
    return path


def get_firestore_client():
    cred_path = _resolve_credentials()
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.Certificate(str(cred_path)))
    return firestore.client()
