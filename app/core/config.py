from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "SecureDesk"
    window_width: int = 1280
    window_height: int = 780
    firebase_credentials: Path = BASE_DIR / "llaveKey.json"
    login_max_attempts: int = 3
    lockout_minutes: int = 15
    session_timeout_minutes: int = 60
    bootstrap_admin_username: str = os.getenv("SECUREDESK_BOOTSTRAP_USER", "admin")
    bootstrap_admin_password: str = os.getenv("SECUREDESK_BOOTSTRAP_PASSWORD", "Admin123!")


CONFIG = AppConfig()
