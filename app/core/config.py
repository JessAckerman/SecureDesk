from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "SecureDesk"
    app_slogan: str = "Tu oficina segura, clara y bajo control."
    window_width: int = 1280
    window_height: int = 780
    firebase_credentials: Path = BASE_DIR / "llaveKey.json"
    login_max_attempts: int = 3
    lockout_minutes: int = int(os.getenv("SECUREDESK_LOCKOUT_MINUTES", "1"))
    session_timeout_seconds: int = 30
    bootstrap_admin_username: str = os.getenv("SECUREDESK_BOOTSTRAP_USER", "admin")
    bootstrap_admin_password: str = os.getenv("SECUREDESK_BOOTSTRAP_PASSWORD", "Admin123!")
    smtp_host: str = os.getenv("SECUREDESK_SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SECUREDESK_SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SECUREDESK_SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SECUREDESK_SMTP_PASSWORD", "")
    smtp_use_tls: bool = os.getenv("SECUREDESK_SMTP_USE_TLS", "true").lower() in {"1", "true", "yes", "on"}
    smtp_from_email: str = os.getenv("SECUREDESK_SMTP_FROM_EMAIL", "")
    smtp_from_name: str = os.getenv("SECUREDESK_SMTP_FROM_NAME", "SecureDesk")


CONFIG = AppConfig()
