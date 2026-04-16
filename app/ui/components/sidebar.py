from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.ui.components.logo_badge import LogoBadge


class Sidebar(ttk.Frame):
    def __init__(self, parent, on_navigate, on_logout, session) -> None:
        super().__init__(parent, style="Sidebar.TFrame", padding=24)
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.session = session
        self._build()

    def _build(self) -> None:
        self.configure(width=250)
        self.pack_propagate(False)

        brand = tk.Frame(self, bg="#0B1F33")
        brand.pack(fill="x", pady=(4, 24))
        LogoBadge(brand, size=64, bg="#0B1F33").pack(anchor="w", pady=(0, 12))

        ttk.Label(self, text="SecureDesk", style="SidebarTitle.TLabel").pack(anchor="w")
        ttk.Label(
            self,
            text="Control administrativo, documental y operativo en un solo entorno seguro.",
            style="Sidebar.TLabel",
            wraplength=190,
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(6, 18))

        badge = tk.Label(
            self,
            text=f"Rol activo: {self.session.role}",
            bg="#16324D",
            fg="#EAF3FF",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=7,
        )
        badge.pack(anchor="w", pady=(0, 22))

        ttk.Label(self, text="NAVEGACION", style="SidebarCaption.TLabel").pack(anchor="w", pady=(0, 8))

        buttons = [("Dashboard", "dashboard"), ("Tareas", "tareas"), ("Documentos", "documentos")]
        if self.session.role == "Administrador":
            buttons.insert(1, ("Usuarios", "usuarios"))
            buttons.append(("Auditoria", "auditoria"))

        for label, key in buttons:
            ttk.Button(
                self,
                text=label,
                style="Nav.TButton",
                command=lambda value=key: self.on_navigate(value),
            ).pack(fill="x", pady=4)

        spacer = tk.Frame(self, bg="#0B1F33")
        spacer.pack(fill="both", expand=True)

        footer = tk.Frame(self, bg="#0B1F33", highlightbackground="#16324D", highlightthickness=1)
        footer.pack(fill="x", pady=(10, 0))
        ttk.Label(
            footer,
            text=self.session.full_name,
            style="Sidebar.TLabel",
        ).pack(anchor="w", padx=12, pady=(12, 2))
        ttk.Label(
            footer,
            text=self.session.username,
            style="SidebarCaption.TLabel",
        ).pack(anchor="w", padx=12, pady=(0, 10))
        ttk.Button(
            footer,
            text="Cerrar sesion",
            style="Logout.TButton",
            command=self.on_logout,
        ).pack(fill="x", padx=10, pady=(0, 12))
