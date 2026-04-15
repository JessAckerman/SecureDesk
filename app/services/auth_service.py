from __future__ import annotations

from datetime import datetime

from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.config import CONFIG
from app.core.security import (
    build_lockout_expiry,
    hash_password,
    sanitize_text,
    utc_now,
    verify_password,
)
from app.core.session import UserSession


class AuthService:
    def __init__(self, db, audit_service) -> None:
        self.db = db
        self.audit_service = audit_service

    def _find_user_doc(self, username: str):
        query = (
            self.db.collection("usuarios")
            .where(filter=FieldFilter("username", "==", sanitize_text(username, 60)))
            .limit(1)
            .stream()
        )
        return next(query, None)

    def login(self, username: str, password: str) -> UserSession:
        user_doc = self._find_user_doc(username)
        if not user_doc:
            self.audit_service.log_event(
                "login_failed",
                sanitize_text(username, 60),
                "Intento fallido por usuario inexistente.",
            )
            raise ValueError("Credenciales incorrectas.")

        data = user_doc.to_dict()
        blocked_until = data.get("blocked_until")
        if isinstance(blocked_until, datetime) and blocked_until > utc_now():
            self.audit_service.log_event(
                "login_blocked",
                data.get("username", "desconocido"),
                "Intento sobre cuenta temporalmente bloqueada.",
                {"blocked_until": blocked_until.isoformat()},
            )
            raise ValueError("Cuenta bloqueada temporalmente. Intenta mas tarde.")

        if data.get("status") == "bloqueado" and (
            not isinstance(blocked_until, datetime) or blocked_until <= utc_now()
        ):
            self.db.collection("usuarios").document(user_doc.id).update(
                {
                    "status": "activo",
                    "blocked_until": None,
                    "failed_attempts": 0,
                    "updated_at": utc_now(),
                }
            )
            data["status"] = "activo"

        if data.get("status") != "activo":
            self.audit_service.log_event(
                "login_denied",
                data.get("username", "desconocido"),
                "Intento de acceso con cuenta no activa.",
                {"status": data.get("status")},
            )
            raise ValueError("La cuenta no esta activa.")

        if not verify_password(
            password,
            data.get("password_hash", ""),
            data.get("password_salt", ""),
        ):
            attempts = int(data.get("failed_attempts", 0)) + 1
            update_payload = {"failed_attempts": attempts, "updated_at": utc_now()}
            description = "Contrasena incorrecta."
            if attempts >= CONFIG.login_max_attempts:
                update_payload["blocked_until"] = build_lockout_expiry(CONFIG.lockout_minutes)
                update_payload["status"] = "bloqueado"
                description = "Cuenta bloqueada por multiples intentos fallidos."
            self.db.collection("usuarios").document(user_doc.id).update(update_payload)
            self.audit_service.log_event(
                "login_failed",
                data.get("username", "desconocido"),
                description,
                {"failed_attempts": attempts},
            )
            raise ValueError("Credenciales incorrectas.")

        self.db.collection("usuarios").document(user_doc.id).update(
            {
                "failed_attempts": 0,
                "blocked_until": None,
                "status": "activo",
                "last_login": utc_now(),
                "updated_at": utc_now(),
            }
        )
        session = UserSession(
            user_id=user_doc.id,
            username=data.get("username", ""),
            full_name=data.get("full_name", ""),
            role=data.get("role", ""),
            must_change_password=bool(data.get("must_change_password", False)),
            accepted_policies=bool(data.get("accepted_policies", False)),
        )
        self.audit_service.log_event(
            "login_success",
            data.get("username", "desconocido"),
            "Inicio de sesion exitoso.",
            {"role": data.get("role", "")},
        )
        return session

    def complete_first_access(
        self,
        session: UserSession,
        new_password: str,
        accept_privacy: bool,
        accept_usage: bool,
    ) -> None:
        if not accept_privacy or not accept_usage:
            raise ValueError("Debes aceptar ambos avisos para continuar.")
        if len(new_password) < 8:
            raise ValueError("La nueva contrasena debe tener al menos 8 caracteres.")

        password_hash, salt = hash_password(new_password)
        self.db.collection("usuarios").document(session.user_id).update(
            {
                "password_hash": password_hash,
                "password_salt": salt,
                "must_change_password": False,
                "accepted_policies": True,
                "accepted_policies_at": utc_now(),
                "updated_at": utc_now(),
            }
        )
        session.must_change_password = False
        session.accepted_policies = True
        self.audit_service.log_event(
            "first_access_completed",
            session.username,
            "El usuario completo el primer acceso y acepto los avisos.",
            {},
        )

    def logout(self, session: UserSession) -> None:
        self.audit_service.log_event(
            "logout",
            session.username,
            "La sesion del usuario fue cerrada.",
            {"session_token": session.token},
        )
