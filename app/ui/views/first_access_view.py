from __future__ import annotations

import tkinter as tk
from tkinter import BooleanVar, StringVar, ttk

from app.core.security import validate_password_policy
from app.ui.components.logo_badge import LogoBadge


class FirstAccessView(ttk.Frame):
    def __init__(self, parent, session, on_continue) -> None:
        super().__init__(parent, style="App.TFrame", padding=28)
        self.session = session
        self.on_continue = on_continue
        self.password_var = StringVar()
        self.privacy_var = BooleanVar(value=False)
        self.usage_var = BooleanVar(value=False)
        self.message_var = StringVar(
            value="Debes cambiar la contrasena provisional y aceptar los avisos."
        )
        self._build()

    def _build(self) -> None:
        wrapper = ttk.Frame(self, style="App.TFrame")
        wrapper.pack(fill="both", expand=True)

        hero = ttk.Frame(wrapper, style="Hero.TFrame", padding=34)
        hero.pack(side="left", fill="both", expand=True)

        content = ttk.Frame(wrapper, style="App.TFrame", padding=0)
        content.pack(side="left", fill="both", expand=True)

        scroll_shell = ttk.Frame(content, style="App.TFrame")
        scroll_shell.pack(fill="both", expand=True, padx=26, pady=26)

        self.scroll_canvas = tk.Canvas(
            scroll_shell,
            bg="#EEF3F8",
            highlightthickness=0,
            bd=0,
        )
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            scroll_shell,
            orient="vertical",
            command=self.scroll_canvas.yview,
        )
        scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.configure(yscrollcommand=scrollbar.set)

        panel_host = ttk.Frame(self.scroll_canvas, style="App.TFrame")
        self.panel_window = self.scroll_canvas.create_window((0, 0), window=panel_host, anchor="nw")
        panel_host.bind(
            "<Configure>",
            lambda _event: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")),
        )
        self.scroll_canvas.bind("<Configure>", self._resize_scroll_content)
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        logo = tk.Frame(hero, bg="#0B1F33")
        logo.pack(anchor="w", pady=(6, 24))
        LogoBadge(logo, size=84, bg="#0B1F33").pack()

        ttk.Label(hero, text="Activacion Segura", style="HeroTitle.TLabel").pack(anchor="w")
        ttk.Label(
            hero,
            text=f"Hola {self.session.full_name}. Vamos a cerrar el proceso de activacion con una contrasena definitiva y aceptacion formal de politicas.",
            style="HeroText.TLabel",
            wraplength=430,
            justify="left",
        ).pack(anchor="w", pady=(12, 22))

        panel = ttk.Frame(panel_host, style="Card.TFrame", padding=30)
        panel.pack(fill="x", expand=True)

        ttk.Label(panel, text="Primer Acceso", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(
            panel,
            text="Completa este paso para habilitar tu cuenta en el entorno corporativo.",
            style="PanelText.TLabel",
            wraplength=720,
        ).pack(anchor="w", pady=(6, 18))

        ttk.Label(panel, text="Nueva contrasena", style="PanelText.TLabel").pack(anchor="w")
        password_entry = ttk.Entry(panel, textvariable=self.password_var, show="*", font=("Segoe UI", 11))
        password_entry.pack(
            fill="x", pady=(4, 16)
        )
        self.password_feedback = ttk.Label(panel, text="Usa mayuscula, minuscula, numero y simbolo.", style="PanelText.TLabel")
        self.password_feedback.pack(anchor="w", pady=(0, 12))
        self.password_var.trace_add("write", lambda *_: self._validate_password())

        for title, text, variable, label in [
            (
                "Aviso de privacidad",
                "SecureDesk recopila y trata datos de acceso, tareas, documentos y eventos de auditoria para fines operativos y de seguridad interna. El uso del sistema implica el tratamiento controlado de esta informacion conforme a las politicas organizacionales y a los principios de confidencialidad e integridad.",
                self.privacy_var,
                "Acepto el aviso de privacidad",
            ),
            (
                "Aviso de uso de la aplicacion",
                "El acceso a SecureDesk es exclusivamente institucional. Todas las acciones realizadas pueden ser registradas en auditoria. El usuario se compromete a usar la aplicacion de forma autorizada, proteger sus credenciales y evitar cualquier alteracion indebida de la informacion.",
                self.usage_var,
                "Acepto el aviso de uso de la aplicacion",
            ),
        ]:
            card = tk.Frame(panel, bg="#F7FAFD", highlightbackground="#D5DFEA", highlightthickness=1)
            card.pack(fill="x", pady=(0, 14))
            ttk.Label(card, text=title, style="PanelTitle.TLabel").pack(anchor="w", padx=16, pady=(14, 8))
            text_widget = tk.Text(card, height=5, wrap="word", font=("Segoe UI", 10), bd=0, bg="#F7FAFD", fg="#5D7288")
            text_widget.pack(fill="x", padx=14, pady=(0, 8))
            text_widget.insert("1.0", text)
            text_widget.configure(state="disabled")
            ttk.Checkbutton(card, text=label, variable=variable).pack(anchor="w", padx=14, pady=(0, 14))

        msg = tk.Frame(panel, bg="#F7FAFD", highlightbackground="#D5DFEA", highlightthickness=1)
        msg.pack(fill="x", pady=(0, 16))
        ttk.Label(
            msg,
            textvariable=self.message_var,
            style="PanelText.TLabel",
            wraplength=720,
        ).pack(anchor="w", padx=14, pady=12)

        ttk.Button(
            panel,
            text="Continuar al sistema",
            style="Primary.TButton",
            command=self._submit,
        ).pack(anchor="e")

    def _resize_scroll_content(self, event) -> None:
        self.scroll_canvas.itemconfigure(self.panel_window, width=event.width)

    def _on_mousewheel(self, event) -> None:
        if self.winfo_exists():
            self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _submit(self) -> None:
        self.on_continue(
            self.password_var.get(),
            self.privacy_var.get(),
            self.usage_var.get(),
        )

    def set_message(self, message: str) -> None:
        self.message_var.set(message)

    def _validate_password(self) -> None:
        valid, message = validate_password_policy(self.password_var.get())
        self.password_feedback.configure(
            text=message,
            style="SuccessFeedback.TLabel" if valid else "ErrorFeedback.TLabel",
        )
