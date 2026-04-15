from __future__ import annotations

from tkinter import StringVar, ttk


class LoginView(ttk.Frame):
    def __init__(self, parent, on_login) -> None:
        super().__init__(parent, style="App.TFrame", padding=40)
        self.on_login = on_login
        self.username_var = StringVar()
        self.password_var = StringVar()
        self.message_var = StringVar(
            value="Ingresa con las credenciales entregadas por el administrador."
        )
        self._build()

    def _build(self) -> None:
        panel = ttk.Frame(self, style="Panel.TFrame", padding=36)
        panel.place(relx=0.5, rely=0.5, anchor="center", width=480, height=360)

        ttk.Label(panel, text="Acceso Seguro", style="PanelTitle.TLabel").pack(
            anchor="w", pady=(0, 8)
        )
        ttk.Label(
            panel,
            text="Solo las cuentas creadas por un administrador pueden ingresar al sistema.",
            style="PanelText.TLabel",
            wraplength=360,
        ).pack(anchor="w", pady=(0, 24))

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

        ttk.Label(
            panel,
            textvariable=self.message_var,
            style="PanelText.TLabel",
            wraplength=360,
        ).pack(anchor="w", pady=(0, 18))

        ttk.Button(
            panel,
            text="Iniciar sesion",
            style="Primary.TButton",
            command=self._submit_login,
        ).pack(fill="x")

    def _submit_login(self) -> None:
        self.on_login(self.username_var.get(), self.password_var.get())

    def set_message(self, message: str) -> None:
        self.message_var.set(message)
