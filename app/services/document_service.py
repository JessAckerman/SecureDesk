from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.security import (
    generate_document_hash,
    sign_document_hash,
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
        user_signature_name: str,
        user_signature_svg: str,
    ) -> None:
        clean_path = sanitize_text(file_path, 260)
        clean_title = sanitize_text(title, 120)
        clean_category = sanitize_text(category, 60)
        clean_task_id = sanitize_text(related_task_id, 80)
        clean_notes = sanitize_multiline(notes, 1200)
        clean_user_signature_name = sanitize_text(user_signature_name, 140)
        clean_user_signature_svg = (user_signature_svg or "").strip()

        if not clean_title:
            raise ValueError("Debes capturar el titulo del documento.")
        if not clean_category:
            raise ValueError("Debes seleccionar una categoria.")
        if not clean_path:
            raise ValueError("Debes seleccionar un archivo.")
        if not Path(clean_path).exists():
            raise ValueError("El archivo seleccionado no existe.")
        if len(clean_user_signature_name) < 5:
            raise ValueError("Debes capturar el nombre del firmante.")
        if not clean_user_signature_svg.startswith("<svg"):
            raise ValueError("Debes capturar la firma del usuario.")

        integrity_hash = generate_document_hash(clean_path)
        digital_signature, signer_identity = sign_document_hash(integrity_hash)

        payload = {
            "title": clean_title,
            "category": clean_category,
            "related_task_id": clean_task_id,
            "file_path": clean_path,
            "integrity_hash": integrity_hash,
            "digital_signature": digital_signature,
            "signed_by": signer_identity,
            "signature_algorithm": "RSA-SHA256",
            "user_signature_name": clean_user_signature_name,
            "user_signature_svg": clean_user_signature_svg,
            "user_signed_at": utc_now(),
            "notes": clean_notes,
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        self.db.collection("documentos").add(payload)
        self.audit_service.log_event(
            "register_document",
            actor,
            f"Se registro el documento {payload['title']} con firma digital.",
            {
                "category": payload["category"],
                "integrity_hash": integrity_hash,
                "signature_algorithm": payload["signature_algorithm"],
                "user_signature_name": clean_user_signature_name,
            },
        )
