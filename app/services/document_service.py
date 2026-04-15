from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.security import (
    generate_document_hash,
    sanitize_multiline,
    sanitize_text,
    utc_now,
)


class DocumentService:
    def __init__(self, db, audit_service) -> None:
        self.db = db
        self.audit_service = audit_service

    def list_documents(self) -> list[dict[str, Any]]:
        items = []
        for doc in self.db.collection("documentos").order_by("created_at").stream():
            data = doc.to_dict()
            data["id"] = doc.id
            items.append(data)
        return items

    def register_document(
        self,
        actor: str,
        title: str,
        category: str,
        related_task_id: str,
        file_path: str,
        notes: str,
    ) -> None:
        clean_path = sanitize_text(file_path, 260)
        integrity_hash = generate_document_hash(clean_path) if clean_path and Path(clean_path).exists() else ""
        payload = {
            "title": sanitize_text(title, 120),
            "category": sanitize_text(category, 60),
            "related_task_id": sanitize_text(related_task_id, 80),
            "file_path": clean_path,
            "integrity_hash": integrity_hash,
            "notes": sanitize_multiline(notes, 1200),
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        self.db.collection("documentos").add(payload)
        self.audit_service.log_event(
            "register_document",
            actor,
            f"Se registró el documento {payload['title']}.",
            {"category": payload["category"], "integrity_hash": integrity_hash},
        )
