from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.ui.components.logo_badge import LogoBadge


class Sidebar(ttk.Frame):
    def __init__(self, parent, on_navigate, on_logout, session) -> None:
        super().__init__(parent, style="Sidebar.TFrame", padding=20)
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.session = session
        self._build()

    def _build(self) -> None:
        logo_wrap = tk.Frame(self, bg="#10324A")
        logo_wrap.pack(anchor="w", pady=(0, 8))
        LogoBadge(logo_wrap, size=58, bg="#10324A").pack(side="left", padx=(0, 10))

        ttk.Label(self, text="SecureDesk", style="SidebarTitle.TLabel").pack(
            anchor="w", pady=(0, 6)
        )
        ttk.Label(
            self,
            text="Gestion segura de tareas y documentos",
            style="Sidebar.TLabel",
            wraplength=180,
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(0, 24))

        buttons = [("Dashboard", "dashboard"), ("Tareas", "tareas"), ("Documentos", "documentos")]
        if self.session.role == "Administrador":
            buttons.insert(1, ("Usuarios", "usuarios"))
            buttons.append(("Auditoria", "auditoria"))

        for label, key in buttons:
            ttk.Button(
                self,
                text=label,
                style="Primary.TButton",
                command=lambda value=key: self.on_navigate(value),
            ).pack(fill="x", pady=6)

        ttk.Label(self, text="", style="Sidebar.TLabel").pack(expand=True, fill="both")
        ttk.Button(
            self,
            text="Cerrar sesion",
            style="Secondary.TButton",
            command=self.on_logout,
        ).pack(fill="x", pady=(12, 0))
