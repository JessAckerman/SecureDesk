from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Any

from app.ui.components.logo_badge import LogoBadge


class SecurityLockView(ttk.Frame):
    def __init__(self, parent, on_return_to_login, blocked_until: Any = None) -> None:
        super().__init__(parent, style="App.TFrame", padding=0)
        self.on_return_to_login = on_return_to_login
        self.blocked_until = self._normalize_blocked_until(blocked_until)
        self.countdown_var = tk.StringVar(value="")
        self._countdown_job = None
        self._build()

    def _build(self) -> None:
        shell = tk.Frame(self, bg="#7F1D1D")
        shell.pack(fill="both", expand=True)

        center = tk.Frame(shell, bg="#FFF5F5", highlightbackground="#C53B3B", highlightthickness=3)
        center.place(relx=0.5, rely=0.5, anchor="center", width=760, height=480)

        header = tk.Frame(center, bg="#9B1C1C", height=92)
        header.pack(fill="x")
        logo_shell = tk.Frame(header, bg="#9B1C1C")
        logo_shell.pack(anchor="w", padx=26, pady=(16, 0))
        LogoBadge(logo_shell, size=62, bg="#9B1C1C").pack(side="left")
        tk.Label(
            logo_shell,
            text="Cuenta comprometida",
            bg="#9B1C1C",
            fg="white",
            font=("Segoe UI Semibold", 28),
        ).pack(side="left", padx=(16, 0))

        body = tk.Frame(center, bg="#FFF5F5")
        body.pack(fill="both", expand=True, padx=34, pady=28)

        tk.Label(
            body,
            text="Se detecto actividad sospechosa y tu sesion fue cerrada por seguridad.",
            bg="#FFF5F5",
            fg="#9B1C1C",
            font=("Segoe UI Semibold", 18),
            wraplength=640,
            justify="left",
        ).pack(anchor="w")

        tk.Label(
            body,
            text=(
                "Tu cuenta fue bloqueada temporalmente. Revisa tu correo para ver la alerta enviada "
                "por SecureDesk. Cuando el tiempo de bloqueo expire, deberas iniciar sesion de nuevo "
                "y completar el cambio obligatorio de contrasena."
            ),
            bg="#FFF5F5",
            fg="#7F1D1D",
            font=("Segoe UI", 12),
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(18, 18))

        steps = [
            "1. Espera a que termine el minuto de bloqueo.",
            "2. Vuelve al login cuando tu cuenta este habilitada.",
            "3. Cambia tu contrasena para reactivar el acceso.",
            "4. Si el problema continua, contacta al administrador.",
        ]
        steps_shell = tk.Frame(body, bg="#FFF5F5")
        steps_shell.pack(fill="x", pady=(0, 24))
        for step in steps:
            tk.Label(
                steps_shell,
                text=step,
                bg="#FFF5F5",
                fg="#5B2121",
                font=("Segoe UI", 12),
                anchor="w",
                justify="left",
            ).pack(anchor="w", pady=4)

        countdown_shell = tk.Frame(body, bg="#FFF5F5")
        countdown_shell.pack(fill="x", pady=(0, 18))
        tk.Label(
            countdown_shell,
            text="Tiempo restante de bloqueo",
            bg="#FFF5F5",
            fg="#9B1C1C",
            font=("Segoe UI Semibold", 13),
        ).pack(anchor="w")
        tk.Label(
            countdown_shell,
            textvariable=self.countdown_var,
            bg="#FFF5F5",
            fg="#7F1D1D",
            font=("Segoe UI Semibold", 24),
        ).pack(anchor="w", pady=(6, 0))

        info = tk.Frame(body, bg="#FDECEC", highlightbackground="#E9B4B4", highlightthickness=1)
        info.pack(fill="x", pady=(0, 24))
        tk.Label(
            info,
            text="El sistema mantuvo evidencia en auditoria y notifico al usuario afectado y a los administradores.",
            bg="#FDECEC",
            fg="#8B2D2D",
            font=("Segoe UI", 11),
            wraplength=620,
            justify="left",
        ).pack(anchor="w", padx=16, pady=14)

        ttk.Button(
            body,
            text="Volver al login",
            style="Primary.TButton",
            command=self.on_return_to_login,
        ).pack(anchor="e")
        self._start_countdown()

    def _start_countdown(self) -> None:
        self._update_countdown()

    def _normalize_blocked_until(self, blocked_until: Any) -> datetime | None:
        if blocked_until is None:
            return None
        if isinstance(blocked_until, datetime):
            if blocked_until.tzinfo is None:
                return blocked_until.astimezone()
            return blocked_until
        if isinstance(blocked_until, str):
            try:
                parsed = datetime.fromisoformat(blocked_until.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    return parsed.astimezone()
                return parsed
            except ValueError:
                return None
        return None

    def _update_countdown(self) -> None:
        if not self.winfo_exists():
            return

        if self.blocked_until is None:
            self.countdown_var.set("01:00")
            return

        remaining = self.blocked_until.astimezone() - datetime.now().astimezone()
        total_seconds = max(0, int(remaining.total_seconds()))
        minutes, seconds = divmod(total_seconds, 60)
        if total_seconds <= 0:
            self.countdown_var.set("Ya puedes volver al login")
            self._countdown_job = self.after(1200, self.on_return_to_login)
            return

        self.countdown_var.set(f"{minutes:02d}:{seconds:02d}")
        self._countdown_job = self.after(1000, self._update_countdown)

    def destroy(self) -> None:
        if self._countdown_job is not None:
            try:
                self.after_cancel(self._countdown_job)
            except Exception:
                pass
            self._countdown_job = None
        super().destroy()
