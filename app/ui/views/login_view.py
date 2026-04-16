from __future__ import annotations

import tkinter as tk
from tkinter import StringVar, ttk

from app.ui.components.logo_badge import LogoBadge


class LoginView(ttk.Frame):
    def __init__(self, parent, on_login) -> None:
        super().__init__(parent, style="App.TFrame", padding=0)
        self.on_login = on_login
        self.username_var = StringVar()
        self.password_var = StringVar()
        self.message_var = StringVar(
            value="Ingresa con las credenciales entregadas por el administrador."
        )
        self._build()

    def _build(self) -> None:
        shell = ttk.Frame(self, style="App.TFrame")
        shell.pack(fill="both", expand=True)

        hero = ttk.Frame(shell, style="Hero.TFrame", padding=42)
        hero.pack(side="left", fill="both", expand=True)

        card_wrap = ttk.Frame(shell, style="App.TFrame", padding=32)
        card_wrap.pack(side="left", fill="both", expand=True)

        hero_logo = tk.Frame(hero, bg="#0B1F33")
        hero_logo.pack(anchor="w", pady=(10, 26))
        LogoBadge(hero_logo, size=90, bg="#0B1F33").pack()

        ttk.Label(hero, text="SecureDesk", style="HeroTitle.TLabel").pack(anchor="w")
        ttk.Label(
            hero,
            text="Plataforma empresarial para control documental, tareas seguras y trazabilidad operativa.",
            style="HeroText.TLabel",
            wraplength=420,
            justify="left",
        ).pack(anchor="w", pady=(12, 24))

        chips = [
            "Seguridad por roles",
            "Firma digital documental",
            "Auditoria de eventos criticos",
        ]
        for chip in chips:
            pill = tk.Label(
                hero,
                text=chip,
                bg="#16324D",
                fg="#EAF3FF",
                font=("Segoe UI", 10, "bold"),
                padx=14,
                pady=8,
            )
            pill.pack(anchor="w", pady=6)

        ttk.Label(
            hero,
            text="Entorno de acceso institucional",
            style="SidebarCaption.TLabel",
        ).pack(anchor="w", pady=(28, 6))
        ttk.Label(
            hero,
            text="Solo personal autorizado puede ingresar al sistema. Cada accion queda bajo control y seguimiento.",
            style="HeroText.TLabel",
            wraplength=430,
            justify="left",
        ).pack(anchor="w")

        panel = ttk.Frame(card_wrap, style="Card.TFrame", padding=38)
        panel.place(relx=0.5, rely=0.5, anchor="center", width=470)

        top = ttk.Frame(panel, style="Card.TFrame")
        top.pack(fill="x", pady=(0, 18))
        ttk.Label(panel, text="Portal De Acceso", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(
            panel,
            text="Identificate para entrar al espacio de trabajo seguro.",
            style="PanelText.TLabel",
            wraplength=340,
        ).pack(anchor="w", pady=(6, 18))

        ttk.Label(panel, text="Usuario", style="PanelText.TLabel").pack(anchor="w")
        ttk.Entry(panel, textvariable=self.username_var, font=("Segoe UI", 11)).pack(
            fill="x", pady=(4, 14)
        )

        ttk.Label(panel, text="Contrasena", style="PanelText.TLabel").pack(anchor="w")
        ttk.Entry(
            panel,
            textvariable=self.password_var,
            show="*",
            font=("Segoe UI", 11),
        ).pack(fill="x", pady=(4, 18))

        info = tk.Frame(panel, bg="#F7FAFD", highlightbackground="#D5DFEA", highlightthickness=1)
        info.pack(fill="x", pady=(0, 18))
        ttk.Label(
            info,
            textvariable=self.message_var,
            style="PanelText.TLabel",
            wraplength=340,
            justify="left",
        ).pack(anchor="w", padx=14, pady=12)

        ttk.Button(
            panel,
            text="Iniciar sesion",
            style="Primary.TButton",
            command=self._submit_login,
        ).pack(fill="x", pady=(4, 0))

    def _submit_login(self) -> None:
        self.on_login(self.username_var.get(), self.password_var.get())

    def set_message(self, message: str) -> None:
        self.message_var.set(message)
