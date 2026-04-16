from __future__ import annotations

import tkinter as tk
from tkinter import StringVar, ttk

from app.ui.components.logo_badge import LogoBadge

try:
    import winsound
except ImportError:  # pragma: no cover - plataforma sin winsound
    winsound = None


class LoginView(ttk.Frame):
    def __init__(self, parent, on_login) -> None:
        super().__init__(parent, style="App.TFrame", padding=0)
        self.on_login = on_login
        self.username_var = StringVar()
        self.password_var = StringVar()
        self.show_password_var = tk.BooleanVar(value=False)
        self.message_var = StringVar(
            value="Ingresa con las credenciales entregadas por el administrador."
        )
        self.message_is_alert = False
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
        password_row = ttk.Frame(panel, style="Card.TFrame")
        password_row.pack(fill="x", pady=(4, 18))
        self.password_entry = ttk.Entry(
            password_row,
            textvariable=self.password_var,
            show="*",
            font=("Segoe UI", 11),
        )
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.password_toggle = ttk.Button(
            password_row,
            text="Ver",
            style="Secondary.TButton",
            command=self._toggle_password_visibility,
            width=10,
        )
        self.password_toggle.pack(side="left", padx=(8, 0))

        self.info_frame = tk.Frame(panel, bg="#F7FAFD", highlightbackground="#D5DFEA", highlightthickness=1)
        self.info_frame.pack(fill="x", pady=(0, 18))
        self.info_label = tk.Label(
            self.info_frame,
            textvariable=self.message_var,
            bg="#F7FAFD",
            fg="#5D7288",
            font=("Segoe UI", 10),
            wraplength=340,
            justify="left",
        )
        self.info_label.pack(anchor="w", padx=14, pady=12)

        ttk.Button(
            panel,
            text="Iniciar sesion",
            style="Primary.TButton",
            command=self._submit_login,
        ).pack(fill="x", pady=(4, 0))

    def _submit_login(self) -> None:
        self.on_login(self.username_var.get(), self.password_var.get())

    def _toggle_password_visibility(self) -> None:
        visible = not self.show_password_var.get()
        self.show_password_var.set(visible)
        self.password_entry.configure(show="" if visible else "*")
        self.password_toggle.configure(text="Ocultar" if visible else "Ver")

    def set_message(self, message: str) -> None:
        self.message_var.set(message)
        is_alert = "ALERTA DE SEGURIDAD" in message.upper()
        if is_alert:
            self.info_frame.configure(bg="#FFF5F5", highlightbackground="#C53B3B", highlightthickness=2)
            self.info_label.configure(bg="#FFF5F5", fg="#9B1C1C", font=("Segoe UI Semibold", 11))
            if winsound and not self.message_is_alert:
                try:
                    winsound.MessageBeep(winsound.MB_ICONHAND)
                except Exception:
                    pass
        else:
            self.info_frame.configure(bg="#F7FAFD", highlightbackground="#D5DFEA", highlightthickness=1)
            self.info_label.configure(bg="#F7FAFD", fg="#5D7288", font=("Segoe UI", 10))
        self.message_is_alert = is_alert
