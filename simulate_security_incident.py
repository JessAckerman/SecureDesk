from __future__ import annotations

from app.core.firebase import get_firestore_client
from app.services.audit_service import AuditService
from app.services.email_service import EmailService
from app.services.security_incident_service import SecurityIncidentService


def main() -> None:
    username = input("Usuario a simular: ").strip()
    if not username:
        raise ValueError("Debes capturar un nombre de usuario.")

    db = get_firestore_client()
    audit_service = AuditService(db)
    email_service = EmailService()
    security_service = SecurityIncidentService(db, audit_service, email_service)

    blocked_until = security_service.trigger_simulated_bruteforce(username)
    print(
        "Incidente simulado correctamente. "
        f"La cuenta fue bloqueada hasta {blocked_until.astimezone().strftime('%Y-%m-%d %H:%M:%S')}."
    )


if __name__ == "__main__":
    main()
