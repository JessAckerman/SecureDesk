from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import CONFIG


class EmailService:
    def __init__(self) -> None:
        self.host = (CONFIG.smtp_host or "").strip()
        self.port = CONFIG.smtp_port
        self.username = (CONFIG.smtp_username or "").strip()
        self.password = CONFIG.smtp_password or ""
        self.use_tls = CONFIG.smtp_use_tls
        self.from_email = (CONFIG.smtp_from_email or self.username).strip()
        self.from_name = (CONFIG.smtp_from_name or CONFIG.app_name).strip()

    def is_configured(self) -> bool:
        return all(
            [
                self.host,
                self.port,
                self.username,
                self.password,
                self.from_email,
            ]
        )

    def _build_message(self, to_email: str, subject: str, body: str) -> EmailMessage:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to_email
        message.set_content(body)
        return message

    def _send_email_message(self, message: EmailMessage) -> None:
        try:
            if self.use_tls:
                with smtplib.SMTP(self.host, self.port, timeout=20) as server:
                    server.starttls(context=ssl.create_default_context())
                    server.login(self.username, self.password)
                    server.send_message(message)
            else:
                with smtplib.SMTP_SSL(self.host, self.port, timeout=20) as server:
                    server.login(self.username, self.password)
                    server.send_message(message)
        except Exception as exc:
            raise ValueError(f"No se pudo enviar el correo: {exc}") from exc

    def _build_html_body(
        self,
        *,
        full_name: str,
        username: str,
        temporary_password: str,
        role: str,
    ) -> str:
        return f"""\
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Acceso a {CONFIG.app_name}</title>
</head>
<body style="margin:0;padding:0;background-color:#eef3f8;font-family:Segoe UI,Arial,sans-serif;color:#16324f;">
  <div style="padding:32px 16px;">
    <div style="max-width:640px;margin:0 auto;background:#ffffff;border:1px solid #d5dfea;border-radius:18px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#1e5aa8 0%,#4aa3d8 100%);padding:28px 32px;color:#ffffff;">
        <div style="font-size:13px;letter-spacing:1.4px;text-transform:uppercase;opacity:.9;">{CONFIG.app_name}</div>
        <h1 style="margin:10px 0 0;font-size:28px;line-height:1.2;">Tu acceso ya fue creado</h1>
      </div>
      <div style="padding:32px;">
        <p style="margin:0 0 16px;font-size:16px;line-height:1.6;">Hola <strong>{full_name}</strong>,</p>
        <p style="margin:0 0 24px;font-size:16px;line-height:1.6;">
          Se registró tu cuenta en <strong>{CONFIG.app_name}</strong>. Aquí tienes tus datos de acceso inicial.
        </p>

        <div style="background:#f6f9fc;border:1px solid #dbe7f3;border-radius:14px;padding:20px 22px;margin-bottom:24px;">
          <div style="margin-bottom:12px;font-size:14px;color:#5b7088;">Usuario</div>
          <div style="margin-bottom:18px;font-size:20px;font-weight:700;color:#16324f;">{username}</div>
          <div style="margin-bottom:12px;font-size:14px;color:#5b7088;">Rol</div>
          <div style="margin-bottom:18px;font-size:18px;font-weight:600;color:#16324f;">{role}</div>
          <div style="margin-bottom:12px;font-size:14px;color:#5b7088;">Contraseña provisional</div>
          <div style="display:inline-block;background:#16324f;color:#ffffff;padding:12px 18px;border-radius:12px;font-size:24px;font-weight:700;letter-spacing:2px;">
            {temporary_password}
          </div>
        </div>

        <div style="background:#fff7e8;border:1px solid #f0d7a1;border-radius:14px;padding:18px 20px;margin-bottom:24px;">
          <p style="margin:0;font-size:15px;line-height:1.6;color:#7a5612;">
            Por seguridad, en tu primer inicio de sesión tendrás que cambiar esta contraseña.
          </p>
        </div>

        <p style="margin:0;font-size:15px;line-height:1.6;color:#5b7088;">
          Si no esperabas este correo, repórtalo con tu administrador.
        </p>
      </div>
    </div>
  </div>
</body>
</html>
"""

    def send_temporary_password(
        self,
        *,
        to_email: str,
        full_name: str,
        username: str,
        temporary_password: str,
        role: str,
    ) -> None:
        if not self.is_configured():
            raise ValueError(
                "El correo no esta configurado. Define SECUREDESK_SMTP_HOST, "
                "SECUREDESK_SMTP_PORT, SECUREDESK_SMTP_USERNAME, "
                "SECUREDESK_SMTP_PASSWORD y SECUREDESK_SMTP_FROM_EMAIL."
            )

        body = (
            f"Hola {full_name},\n\n"
            f"Se creo tu acceso a {CONFIG.app_name}.\n\n"
            f"Usuario: {username}\n"
            f"Rol: {role}\n"
            f"Contrasena provisional: {temporary_password}\n\n"
            "Por seguridad, deberas cambiar esta contrasena en tu primer inicio de sesion.\n"
        )
        message = self._build_message(
            to_email,
            f"Acceso a {CONFIG.app_name}",
            body,
        )
        message.add_alternative(
            self._build_html_body(
                full_name=full_name,
                username=username,
                temporary_password=temporary_password,
                role=role,
            ),
            subtype="html",
        )
        self._send_email_message(message)

    def send_security_alert_user(
        self,
        *,
        to_email: str,
        full_name: str,
        username: str,
        blocked_until_text: str,
    ) -> None:
        if not self.is_configured():
            raise ValueError("El correo no esta configurado para enviar alertas de seguridad.")

        body = (
            f"Hola {full_name},\n\n"
            "Detectamos multiples intentos fallidos de acceso a tu cuenta.\n\n"
            f"Usuario: {username}\n"
            f"Bloqueo temporal hasta: {blocked_until_text}\n\n"
            "Tu cuenta fue bloqueada temporalmente por seguridad. Cuando el bloqueo expire, "
            "deberas cambiar tu contrasena antes de volver a usar el sistema.\n"
        )
        message = self._build_message(
            to_email,
            f"Alerta de seguridad en {CONFIG.app_name}",
            body,
        )
        message.add_alternative(
            f"""\
<!DOCTYPE html>
<html lang="es">
<body style="margin:0;padding:24px;background:#eef3f8;font-family:Segoe UI,Arial,sans-serif;color:#172635;">
  <div style="max-width:640px;margin:0 auto;background:#ffffff;border:1px solid #d5dfea;border-radius:18px;overflow:hidden;">
    <div style="background:linear-gradient(135deg,#b91c1c 0%,#ef4444 100%);padding:28px 32px;color:#ffffff;">
      <div style="font-size:13px;letter-spacing:1.2px;text-transform:uppercase;opacity:.92;">{CONFIG.app_name}</div>
      <h1 style="margin:10px 0 0;font-size:28px;">Alerta de seguridad</h1>
    </div>
    <div style="padding:32px;">
      <p style="font-size:16px;line-height:1.6;">Hola <strong>{full_name}</strong>, detectamos multiples intentos fallidos de acceso a tu cuenta.</p>
      <div style="background:#fff5f5;border:1px solid #fecaca;border-radius:14px;padding:20px 22px;margin:20px 0;">
        <div style="font-size:14px;color:#7f1d1d;margin-bottom:10px;">Usuario</div>
        <div style="font-size:20px;font-weight:700;margin-bottom:16px;">{username}</div>
        <div style="font-size:14px;color:#7f1d1d;margin-bottom:10px;">Bloqueo temporal hasta</div>
        <div style="font-size:18px;font-weight:700;">{blocked_until_text}</div>
      </div>
      <p style="font-size:15px;line-height:1.6;color:#5d7288;">Por seguridad, tu cuenta fue bloqueada temporalmente. Cuando el bloqueo expire, tendras que cambiar tu contrasena antes de volver a ingresar.</p>
    </div>
  </div>
</body>
</html>
""",
            subtype="html",
        )
        self._send_email_message(message)

    def send_security_alert_admin(
        self,
        *,
        to_email: str,
        target_username: str,
        target_email: str,
        blocked_until_text: str,
    ) -> None:
        if not self.is_configured():
            raise ValueError("El correo no esta configurado para enviar alertas de seguridad.")

        body = (
            "Se detecto un incidente de seguridad por multiples intentos fallidos de acceso.\n\n"
            f"Usuario afectado: {target_username}\n"
            f"Correo: {target_email}\n"
            f"Bloqueo temporal hasta: {blocked_until_text}\n\n"
            "La cuenta fue bloqueada y se forzo cambio de contrasena en el siguiente acceso valido.\n"
        )
        message = self._build_message(
            to_email,
            f"Incidente de seguridad en {CONFIG.app_name}",
            body,
        )
        self._send_email_message(message)
