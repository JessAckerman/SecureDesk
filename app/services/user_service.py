from __future__ import annotations

import re
from typing import Any

from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.security import hash_password, sanitize_text, utc_now, validate_email


class UserService:
    USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{4,30}$")

    def __init__(self, db, audit_service) -> None:
        self.db = db
        self.audit_service = audit_service

    def _validate_password_strength(self, password: str) -> None:
        if len(password) < 8:
            raise ValueError("La contrasena provisional debe tener al menos 8 caracteres.")
        if not any(char.isupper() for char in password):
            raise ValueError("La contrasena provisional debe incluir al menos una mayuscula.")
        if not any(char.islower() for char in password):
            raise ValueError("La contrasena provisional debe incluir al menos una minuscula.")
        if not any(char.isdigit() for char in password):
            raise ValueError("La contrasena provisional debe incluir al menos un numero.")
        if not any(char in "!@#$%^&*()-_=+[]{};:,.?" for char in password):
            raise ValueError("La contrasena provisional debe incluir al menos un simbolo.")

    def bootstrap_admin(self, username: str, password: str) -> None:
        existing = list(self.db.collection("usuarios").limit(1).stream())
        if existing:
            return
        password_hash, salt = hash_password(password)
        payload = {
            "username": sanitize_text(username, 60),
            "full_name": "Administrador Inicial",
            "email": "admin@securedesk.local",
            "role": "Administrador",
            "status": "activo",
            "password_hash": password_hash,
            "password_salt": salt,
            "failed_attempts": 0,
            "blocked_until": None,
            "must_change_password": False,
            "accepted_policies": True,
            "accepted_policies_at": utc_now(),
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        self.db.collection("usuarios").add(payload)
        self.audit_service.log_event(
            "bootstrap_admin",
            "system",
            "Se creo el usuario administrador inicial.",
            {"username": username},
        )

    def list_users(self) -> list[dict[str, Any]]:
        items = []
        for doc in self.db.collection("usuarios").order_by("created_at").stream():
            data = doc.to_dict()
            data["id"] = doc.id
            items.append(data)
        return items

    def create_user(
        self,
        actor: str,
        username: str,
        full_name: str,
        email: str,
        role: str,
        password: str,
    ) -> None:
        username = sanitize_text(username, 60)
        full_name = sanitize_text(full_name, 120)
        email = sanitize_text(email, 120).lower()
        role = sanitize_text(role, 50)

        if not username:
            raise ValueError("Debes capturar el nombre de usuario.")
        if not self.USERNAME_RE.fullmatch(username):
            raise ValueError("El usuario debe tener entre 4 y 30 caracteres y solo puede usar letras, numeros, punto, guion y guion bajo.")
        if len(full_name) < 5:
            raise ValueError("El nombre completo debe tener al menos 5 caracteres.")
        if not validate_email(email):
            raise ValueError("El correo electronico no es valido.")
        if role not in {"Administrador", "Usuario"}:
            raise ValueError("El rol seleccionado no es valido.")
        self._validate_password_strength(password)

        duplicated = (
            self.db.collection("usuarios")
            .where(filter=FieldFilter("username", "==", username))
            .limit(1)
            .stream()
        )
        if any(True for _ in duplicated):
            raise ValueError("El nombre de usuario ya existe.")

        duplicated_email = (
            self.db.collection("usuarios")
            .where(filter=FieldFilter("email", "==", email))
            .limit(1)
            .stream()
        )
        if any(True for _ in duplicated_email):
            raise ValueError("El correo electronico ya esta registrado.")

        password_hash, salt = hash_password(password)
        payload = {
            "username": username,
            "full_name": full_name,
            "email": email,
            "role": role,
            "status": "activo",
            "password_hash": password_hash,
            "password_salt": salt,
            "failed_attempts": 0,
            "blocked_until": None,
            "must_change_password": True,
            "accepted_policies": False,
            "accepted_policies_at": None,
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        self.db.collection("usuarios").add(payload)
        self.audit_service.log_event(
            "create_user",
            actor,
            f"Se registro el usuario {username} con contrasena provisional.",
            {"username": username, "role": role},
        )

    def update_status(self, actor: str, user_id: str, status: str) -> None:
        status = sanitize_text(status, 30).lower()
        if status not in {"activo", "bloqueado", "inactivo"}:
            raise ValueError("Estado no permitido.")
        self.db.collection("usuarios").document(user_id).update(
            {"status": status, "updated_at": utc_now()}
        )
        self.audit_service.log_event(
            "update_user_status",
            actor,
            f"Se actualizo el estado del usuario {user_id} a {status}.",
            {"user_id": user_id, "status": status},
        )
