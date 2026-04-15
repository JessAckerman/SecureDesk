from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserRecord:
    user_id: str
    username: str
    full_name: str
    email: str
    role: str
    status: str
    created_at: datetime | None = None


@dataclass
class TaskRecord:
    task_id: str
    title: str
    priority: str
    status: str
    due_date: str
    assigned_to: str


@dataclass
class DocumentRecord:
    document_id: str
    title: str
    category: str
    related_task_id: str
    integrity_hash: str


@dataclass
class AuditRecord:
    audit_id: str
    event_type: str
    actor: str
    description: str
    created_at: datetime | None = None
