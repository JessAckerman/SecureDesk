from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.core.config import CONFIG
from app.core.firebase import get_firestore_client
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.document_service import DocumentService
from app.services.task_service import TaskService
from app.services.user_service import UserService
from app.ui.components.sidebar import Sidebar
from app.ui.theme import apply_theme
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.first_access_view import FirstAccessView
from app.ui.views.login_view import LoginView


class SecureDeskApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(CONFIG.app_name)
        self.geometry(f"{CONFIG.window_width}x{CONFIG.window_height}")
        self.minsize(1100, 700)
        apply_theme(self)

        self.db = get_firestore_client()
        self.audit_service = AuditService(self.db)
        self.user_service = UserService(self.db, self.audit_service)
        self.auth_service = AuthService(self.db, self.audit_service)
        self.task_service = TaskService(self.db, self.audit_service)
        self.document_service = DocumentService(self.db, self.audit_service)
        self.services = {
            "audit": self.audit_service,
            "users": self.user_service,
            "auth": self.auth_service,
            "tasks": self.task_service,
            "documents": self.document_service,
        }
        self.user_service.bootstrap_admin(
            CONFIG.bootstrap_admin_username,
            CONFIG.bootstrap_admin_password,
        )

        self.session = None
        self.container = ttk.Frame(self, style="App.TFrame")
        self.container.pack(fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.show_login()

    def clear_container(self) -> None:
        for child in self.container.winfo_children():
            child.destroy()

    def show_login(self) -> None:
        self.clear_container()
        self.login_view = LoginView(self.container, self.handle_login)
        self.login_view.pack(fill="both", expand=True)

    def handle_login(self, username: str, password: str) -> None:
        try:
            self.session = self.auth_service.login(username, password)
            if self.session.must_change_password or not self.session.accepted_policies:
                self.show_first_access()
            else:
                self.show_dashboard()
        except Exception as exc:
            self.login_view.set_message(str(exc))

    def show_first_access(self) -> None:
        self.clear_container()
        self.first_access_view = FirstAccessView(
            self.container,
            self.session,
            self.handle_first_access,
        )
        self.first_access_view.pack(fill="both", expand=True)

    def handle_first_access(
        self,
        new_password: str,
        accept_privacy: bool,
        accept_usage: bool,
    ) -> None:
        try:
            self.auth_service.complete_first_access(
                self.session,
                new_password,
                accept_privacy,
                accept_usage,
            )
            self.show_dashboard()
        except Exception as exc:
            self.first_access_view.set_message(str(exc))

    def show_dashboard(self) -> None:
        self.clear_container()

        shell = ttk.Frame(self.container, style="App.TFrame")
        shell.pack(fill="both", expand=True)

        sidebar = Sidebar(shell, self.navigate, self.logout, self.session)
        sidebar.pack(side="left", fill="y")

        self.dashboard = DashboardView(shell, self.services, self.session)
        self.dashboard.pack(side="left", fill="both", expand=True)

    def navigate(self, section: str) -> None:
        if not self.session:
            return
        if self.session.is_expired():
            messagebox.showwarning(
                CONFIG.app_name,
                "La sesion expiro por inactividad. Vuelve a iniciar sesion.",
            )
            self.logout()
            return
        self.session.touch()
        if section in {"usuarios", "auditoria"} and self.session.role != "Administrador":
            messagebox.showwarning(
                CONFIG.app_name,
                "No tienes permisos para acceder a esta seccion.",
            )
            return
        self.dashboard.show_section(section)

    def logout(self) -> None:
        if self.session:
            self.auth_service.logout(self.session)
        self.session = None
        self.show_login()

    def _on_close(self) -> None:
        if self.session:
            self.auth_service.logout(self.session)
        self.destroy()
