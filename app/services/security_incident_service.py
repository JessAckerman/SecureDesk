from __future__ import annotations

from datetime import datetime

from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.config import CONFIG
from app.core.security import build_lockout_expiry, utc_now, validate_email


class SecurityIncidentService:
    def __init__(self, db, audit_service, email_service) -> None:
        self.db = db
        self.audit_service = audit_service
        self.email_service = email_service

    def _blocked_until_text(self, blocked_until: datetime) -> str:
        return blocked_until.astimezone().strftime("%Y-%m-%d %H:%M:%S")

    def _admin_recipients(self, excluded_email: str | None = None) -> list[str]:
        docs = (
            self.db.collection("usuarios")
            .where(filter=FieldFilter("role", "==", "Administrador"))
            .stream()
        )
        emails: list[str] = []
        for doc in docs:
            email = (doc.to_dict().get("email") or "").strip().lower()
            if not validate_email(email):
                continue
            if excluded_email and email == excluded_email.lower():
                continue
            if email not in emails:
                emails.append(email)
        return emails

    def trigger_bruteforce_lock(
        self,
        *,
        user_doc_id: str,
        user_data: dict,
        attempts: int,
        source: str,
        simulated: bool = False,
    ) -> datetime:
        blocked_until = build_lockout_expiry(CONFIG.lockout_minutes)
        security_message = (
            "ALERTA DE SEGURIDAD: Detectamos multiples intentos fallidos de acceso. "
            "Tu cuenta fue bloqueada temporalmente y deberas cambiar tu contrasena "
            "cuando el bloqueo expire."
        )

        self.db.collection("usuarios").document(user_doc_id).update(
            {
                "failed_attempts": attempts,
                "blocked_until": blocked_until,
                "status": "bloqueado",
                "must_change_password": True,
                "security_alert_active": True,
                "security_alert_message": security_message,
                "updated_at": utc_now(),
            }
        )

        username = user_data.get("username", "desconocido")
        email = (user_data.get("email") or "").strip().lower()
        full_name = user_data.get("full_name", username)
        blocked_until_text = self._blocked_until_text(blocked_until)
        incident_type = "simulado" if simulated else "detectado"

        self.audit_service.log_event(
            "security_bruteforce_detected",
            source,
            f"Se {incident_type} un intento de fuerza bruta sobre la cuenta {username}. La cuenta fue bloqueada.",
            {
                "username": username,
                "email": email,
                "attempts": attempts,
                "blocked_until": blocked_until.isoformat(),
                "simulated": simulated,
            },
        )

        if self.email_service.is_configured():
            if validate_email(email):
                try:
                    self.email_service.send_security_alert_user(
                        to_email=email,
                        full_name=full_name,
                        username=username,
                        blocked_until_text=blocked_until_text,
                    )
                except Exception as exc:
                    self.audit_service.log_event(
                        "security_notification_failed",
                        source,
                        f"No se pudo notificar al usuario {username} sobre el incidente de seguridad.",
                        {"error": str(exc), "username": username},
                    )

            for admin_email in self._admin_recipients(excluded_email=email):
                try:
                    self.email_service.send_security_alert_admin(
                        to_email=admin_email,
                        target_username=username,
                        target_email=email,
                        blocked_until_text=blocked_until_text,
                    )
                except Exception as exc:
                    self.audit_service.log_event(
                        "security_notification_failed",
                        source,
                        f"No se pudo notificar al administrador {admin_email} sobre el incidente de seguridad.",
                        {"error": str(exc), "admin_email": admin_email, "username": username},
                    )

        return blocked_until

    def trigger_simulated_bruteforce(self, username: str) -> datetime:
        query = (
            self.db.collection("usuarios")
            .where(filter=FieldFilter("username", "==", username.strip()))
            .limit(1)
            .stream()
        )
        user_doc = next(query, None)
        if not user_doc:
            raise ValueError("No se encontro el usuario para simular el incidente.")
        return self.trigger_bruteforce_lock(
            user_doc_id=user_doc.id,
            user_data=user_doc.to_dict(),
            attempts=CONFIG.login_max_attempts,
            source="security-simulator",
            simulated=True,
        )
