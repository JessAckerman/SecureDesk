from __future__ import annotations

from typing import Any

from firebase_admin import firestore

from app.core.security import sanitize_multiline, sanitize_text, utc_now


class AuditService:
    def __init__(self, db) -> None:
        self.db = db

    def log_event(
        self,
        event_type: str,
        actor: str,
        description: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "event_type": sanitize_text(event_type, 80),
            "actor": sanitize_text(actor, 120),
            "description": sanitize_multiline(description, 800),
            "metadata": metadata or {},
            "created_at": utc_now(),
        }
        self.db.collection("auditoria").add(payload)

    def list_events(self, limit: int = 100) -> list[dict[str, Any]]:
        docs = (
            self.db.collection("auditoria")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        items = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            items.append(data)
        return items
