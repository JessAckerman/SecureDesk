from __future__ import annotations

import tkinter as tk
from tkinter import BooleanVar, StringVar, ttk


class FirstAccessView(ttk.Frame):
    def __init__(self, parent, session, on_continue) -> None:
        super().__init__(parent, style="App.TFrame", padding=32)
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
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        panel = ttk.Frame(wrapper, style="Panel.TFrame", padding=28)
        panel.pack(fill="both", expand=True)

        ttk.Label(panel, text="Primer Acceso", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(
            panel,
            text=f"Bienvenido {self.session.full_name}. Antes de entrar debes completar este paso.",
            style="PanelText.TLabel",
            wraplength=760,
        ).pack(anchor="w", pady=(6, 18))

        ttk.Label(panel, text="Nueva contrasena", style="PanelText.TLabel").pack(anchor="w")
        ttk.Entry(panel, textvariable=self.password_var, show="*", font=("Segoe UI", 11)).pack(
            fill="x", pady=(4, 16)
        )

        ttk.Label(panel, text="Aviso de privacidad", style="PanelTitle.TLabel").pack(anchor="w")
        privacy_text = tk.Text(panel, height=6, wrap="word", font=("Segoe UI", 10))
        privacy_text.pack(fill="x", pady=(6, 8))
        privacy_text.insert(
            "1.0",
            "SecureDesk recopila y trata datos de acceso, tareas, documentos y eventos "
            "de auditoria para fines operativos y de seguridad interna. El uso del sistema "
            "implica el tratamiento controlado de esta informacion conforme a las politicas "
            "organizacionales y a los principios de confidencialidad e integridad.",
        )
        privacy_text.configure(state="disabled")
        ttk.Checkbutton(
            panel,
            text="Acepto el aviso de privacidad",
            variable=self.privacy_var,
        ).pack(anchor="w", pady=(0, 16))

        ttk.Label(panel, text="Aviso de uso de la aplicacion", style="PanelTitle.TLabel").pack(anchor="w")
        usage_text = tk.Text(panel, height=6, wrap="word", font=("Segoe UI", 10))
        usage_text.pack(fill="x", pady=(6, 8))
        usage_text.insert(
            "1.0",
            "El acceso a SecureDesk es exclusivamente institucional. Todas las acciones "
            "realizadas pueden ser registradas en auditoria. El usuario se compromete a "
            "usar la aplicacion de forma autorizada, proteger sus credenciales y evitar "
            "cualquier alteracion indebida de la informacion.",
        )
        usage_text.configure(state="disabled")
        ttk.Checkbutton(
            panel,
            text="Acepto el aviso de uso de la aplicacion",
            variable=self.usage_var,
        ).pack(anchor="w", pady=(0, 16))

        ttk.Label(
            panel,
            textvariable=self.message_var,
            style="PanelText.TLabel",
            wraplength=760,
        ).pack(anchor="w", pady=(0, 16))

        ttk.Button(
            panel,
            text="Continuar al sistema",
            style="Primary.TButton",
            command=self._submit,
        ).pack(anchor="e")

    def _submit(self) -> None:
        self.on_continue(
            self.password_var.get(),
            self.privacy_var.get(),
            self.usage_var.get(),
        )

    def set_message(self, message: str) -> None:
        self.message_var.set(message)
