from __future__ import annotations

import tkinter as tk
from tkinter import StringVar, ttk

from app.core.config import CONFIG
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
        shell = tk.Frame(self, bg="#071827")
        shell.pack(fill="both", expand=True)

        self._paint_background(shell)

        header = tk.Frame(shell, bg="#071827")
        header.pack(fill="x", padx=42, pady=(28, 0))

        brand = tk.Frame(header, bg="#071827")
        brand.pack(side="left")
        LogoBadge(brand, size=58, bg="#071827").pack(side="left")
        brand_text = tk.Frame(brand, bg="#071827")
        brand_text.pack(side="left", padx=(14, 0))
        tk.Label(
            brand_text,
            text=CONFIG.app_name,
            bg="#071827",
            fg="#FFFFFF",
            font=("Segoe UI Semibold", 22),
        ).pack(anchor="w")
        tk.Label(
            brand_text,
            text=CONFIG.app_slogan,
            bg="#071827",
            fg="#99B7D2",
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Acceso institucional",
            bg="#0E2A43",
            fg="#DFF3FF",
            font=("Segoe UI Semibold", 10),
            padx=16,
            pady=9,
        ).pack(side="right")

        body = tk.Frame(shell, bg="#071827")
        body.pack(fill="both", expand=True, padx=42, pady=24)

        hero = tk.Frame(body, bg="#071827")
        hero.pack(side="left", fill="both", expand=True, padx=(0, 34))

        hero_inner = tk.Frame(hero, bg="#071827")
        hero_inner.place(relx=0, rely=0.46, anchor="w")

        tk.Label(
            hero_inner,
            text="Controla el trabajo,\nprotege cada registro.",
            bg="#071827",
            fg="#FFFFFF",
            font=("Segoe UI Semibold", 42),
            justify="left",
        ).pack(anchor="w")
        tk.Label(
            hero_inner,
            text=(
                "SecureDesk centraliza usuarios, tareas, documentos y seguimiento operativo "
                "en una experiencia clara para equipos que necesitan orden y evidencia."
            ),
            bg="#071827",
            fg="#B9D2E8",
            font=("Segoe UI", 13),
            wraplength=540,
            justify="left",
        ).pack(anchor="w", pady=(18, 26))

        metrics = tk.Frame(hero_inner, bg="#071827")
        metrics.pack(anchor="w")
        for value, label, color in [
            ("01", "Portal unico", "#4AA3D8"),
            ("24/7", "Trazabilidad", "#29B59F"),
            ("RSA", "Firma digital", "#F0B75E"),
        ]:
            card = tk.Frame(metrics, bg="#0E2A43", highlightbackground="#1C4868", highlightthickness=1)
            card.pack(side="left", padx=(0, 12))
            tk.Frame(card, bg=color, height=4).pack(fill="x")
            tk.Label(
                card,
                text=value,
                bg="#0E2A43",
                fg="#FFFFFF",
                font=("Segoe UI Semibold", 17),
                padx=18,
            ).pack(anchor="w", pady=(12, 0))
            tk.Label(
                card,
                text=label,
                bg="#0E2A43",
                fg="#A8C0D6",
                font=("Segoe UI", 9),
                padx=18,
            ).pack(anchor="w", pady=(0, 12))

        card_wrap = tk.Frame(body, bg="#071827")
        card_wrap.pack(side="left", fill="both", expand=True)

        panel_shadow = tk.Frame(card_wrap, bg="#06121E")
        panel_shadow.place(relx=0.52, rely=0.51, anchor="center", width=482, height=494)

        panel = tk.Frame(card_wrap, bg="#FFFFFF", highlightbackground="#CFE0EF", highlightthickness=1)
        panel.place(relx=0.5, rely=0.5, anchor="center", width=482, height=494)

        tk.Frame(panel, bg="#1E5AA8", height=7).pack(fill="x")

        panel_body = tk.Frame(panel, bg="#FFFFFF")
        panel_body.pack(fill="both", expand=True, padx=38, pady=30)

        tk.Label(
            panel_body,
            text="Bienvenido de nuevo",
            bg="#FFFFFF",
            fg="#0B1F33",
            font=("Segoe UI Semibold", 25),
        ).pack(anchor="w")
        tk.Label(
            panel_body,
            text="Ingresa tus credenciales para abrir tu espacio de trabajo.",
            bg="#FFFFFF",
            fg="#5D7288",
            font=("Segoe UI", 10),
            wraplength=360,
            justify="left",
        ).pack(anchor="w", pady=(6, 22))

        tk.Label(
            panel_body,
            text="Usuario",
            bg="#FFFFFF",
            fg="#40566B",
            font=("Segoe UI Semibold", 10),
        ).pack(anchor="w")
        ttk.Entry(panel_body, textvariable=self.username_var, font=("Segoe UI", 11)).pack(
            fill="x", pady=(4, 14)
        )

        tk.Label(
            panel_body,
            text="Contrasena",
            bg="#FFFFFF",
            fg="#40566B",
            font=("Segoe UI Semibold", 10),
        ).pack(anchor="w")
        password_row = tk.Frame(panel_body, bg="#FFFFFF")
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

        self.info_frame = tk.Frame(panel_body, bg="#F7FAFD", highlightbackground="#D5DFEA", highlightthickness=1)
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
            panel_body,
            text="Iniciar sesion",
            style="Primary.TButton",
            command=self._submit_login,
        ).pack(fill="x", pady=(4, 0))

        tk.Label(
            panel_body,
            text="Personal autorizado unicamente",
            bg="#FFFFFF",
            fg="#8AA0B4",
            font=("Segoe UI", 9),
        ).pack(anchor="center", pady=(18, 0))

        footer = tk.Frame(shell, bg="#071827")
        footer.pack(fill="x", padx=42, pady=(0, 24))
        tk.Label(
            footer,
            text=f"{CONFIG.app_name} - {CONFIG.app_slogan}",
            bg="#071827",
            fg="#99B7D2",
            font=("Segoe UI", 9),
        ).pack(side="left")
        tk.Label(
            footer,
            text="Gestion interna | Documentos | Tareas | Auditoria",
            bg="#071827",
            fg="#5F7F99",
            font=("Segoe UI", 9),
        ).pack(side="right")

    def _paint_background(self, parent) -> None:
        canvas = tk.Canvas(parent, bg="#071827", highlightthickness=0, bd=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        canvas.create_rectangle(0, 0, 900, 900, fill="#071827", outline="")
        canvas.create_polygon(0, 0, 720, 0, 520, 900, 0, 900, fill="#0B1F33", outline="")
        canvas.create_polygon(0, 0, 380, 0, 230, 900, 0, 900, fill="#123A5A", outline="")
        canvas.create_line(650, 80, 1120, 720, fill="#1C4868", width=2)
        canvas.create_line(760, 20, 1210, 650, fill="#10324A", width=2)
        canvas.create_oval(980, -160, 1360, 220, fill="#0E2A43", outline="")
        canvas.create_oval(1040, -95, 1250, 115, fill="#123A5A", outline="")
        canvas.tk.call("lower", canvas._w)

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
