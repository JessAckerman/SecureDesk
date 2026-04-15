from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.core.config import CONFIG
from app.core.security import generate_session_token, utc_now


@dataclass
class UserSession:
    user_id: str
    username: str
    full_name: str
    role: str
    must_change_password: bool = False
    accepted_policies: bool = False
    token: str = field(default_factory=generate_session_token)
    created_at: datetime = field(default_factory=utc_now)
    last_activity: datetime = field(default_factory=utc_now)

    def touch(self) -> None:
        self.last_activity = utc_now()

    def is_expired(self) -> bool:
        timeout = timedelta(minutes=CONFIG.session_timeout_minutes)
        return utc_now() > self.last_activity + timeout
