from __future__ import annotations

from typing import Any

from app.core.security import sanitize_multiline, sanitize_text, utc_now


class TaskService:
    def __init__(self, db, audit_service) -> None:
        self.db = db
        self.audit_service = audit_service

    def list_tasks(self) -> list[dict[str, Any]]:
        items = []
        for doc in self.db.collection("tareas").order_by("created_at").stream():
            data = doc.to_dict()
            data["id"] = doc.id
            items.append(data)
        return items

    def create_task(
        self,
        actor: str,
        title: str,
        description: str,
        priority: str,
        status: str,
        due_date: str,
        assigned_to: str,
    ) -> None:
        payload = {
            "title": sanitize_text(title, 120),
            "description": sanitize_multiline(description, 1200),
            "priority": sanitize_text(priority, 20),
            "status": sanitize_text(status, 30),
            "due_date": sanitize_text(due_date, 20),
            "assigned_to": sanitize_text(assigned_to, 80),
            "evidence_count": 0,
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        self.db.collection("tareas").add(payload)
        self.audit_service.log_event(
            "create_task",
            actor,
            f"Se creó la tarea {payload['title']}.",
            {"priority": payload["priority"], "status": payload["status"]},
        )

    def update_task_status(self, actor: str, task_id: str, status: str) -> None:
        status = sanitize_text(status, 30)
        self.db.collection("tareas").document(task_id).update(
            {"status": status, "updated_at": utc_now()}
        )
        self.audit_service.log_event(
            "update_task_status",
            actor,
            f"Se actualizó el estado de la tarea {task_id} a {status}.",
            {"task_id": task_id, "status": status},
        )
