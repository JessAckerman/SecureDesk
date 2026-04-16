from __future__ import annotations

from datetime import date, timedelta
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.core.security import validate_email
from app.ui.components.signature_pad import SignaturePad

try:
    import winsound
except ImportError:  # pragma: no cover - plataforma sin winsound
    winsound = None


class DashboardView(ttk.Frame):
    USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{4,30}$")
    SECURITY_POLL_MS = 3000

    def __init__(self, parent, services, session, on_forced_logout) -> None:
        super().__init__(parent, style="App.TFrame", padding=24)
        self.services = services
        self.session = session
        self.on_forced_logout = on_forced_logout
        self.current_section = None
        self.file_path_var = tk.StringVar()
        self.task_due_dates = self._build_due_date_options()
        self.task_priorities = ["Baja", "Media", "Alta", "Critica"]
        self.task_statuses = ["Pendiente", "En progreso", "En revision", "Completada", "Bloqueada"]
        self.document_categories = [
            "Contrato",
            "Reporte",
            "Evidencia",
            "Politica interna",
            "Manual",
            "Acta",
            "Otro",
        ]
        self.user_roles = ["Administrador", "Usuario"]
        self.security_banner = None
        self._security_poll_job = None
        self._security_alert_seen = bool(getattr(self.session, "security_alert_active", False))
        self._security_logout_in_progress = False
        self._build()

    def _build_due_date_options(self) -> list[str]:
        options = ["Sin fecha"]
        today = date.today()
        for offset in range(0, 31):
            options.append((today + timedelta(days=offset)).isoformat())
        return options

    def _build(self) -> None:
        header = ttk.Frame(self, style="App.TFrame")
        header.pack(fill="x", pady=(0, 16))
        ttk.Label(header, text="Panel Principal", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text=f"Vista ejecutiva activa para {self.session.full_name} ({self.session.role})",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        banner = tk.Frame(self, bg="#FFFFFF", highlightbackground="#D5DFEA", highlightthickness=1)
        banner.pack(fill="x", pady=(0, 18))
        accent = tk.Frame(banner, bg="#1E5AA8", width=8)
        accent.pack(side="left", fill="y")
        banner_body = ttk.Frame(banner, style="Card.TFrame", padding=18)
        banner_body.pack(side="left", fill="both", expand=True)
        ttk.Label(
            banner_body,
            text="Centro de mando corporativo",
            style="PanelTitle.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            banner_body,
            text="Supervisa usuarios, operaciones, documentos firmados y eventos criticos desde una experiencia mas clara y profesional.",
            style="PanelText.TLabel",
            wraplength=980,
        ).pack(anchor="w", pady=(4, 0))

        stats = ttk.Frame(self, style="App.TFrame")
        stats.pack(fill="x", pady=(0, 20))
        card_titles = ["Tareas", "Documentos"]
        if self.session.role == "Administrador":
            card_titles = ["Usuarios", "Tareas", "Documentos", "Auditoria"]
        self.stats_labels = {}
        for title in card_titles:
            card_shell = tk.Frame(stats, bg="#FFFFFF", highlightbackground="#D5DFEA", highlightthickness=1)
            card_shell.pack(side="left", expand=True, fill="both", padx=(0, 10))
            color = "#1E5AA8"
            if title == "Usuarios":
                color = "#4AA3D8"
            elif title == "Documentos":
                color = "#0F766E"
            elif title == "Auditoria":
                color = "#C18A2C"
            tk.Frame(card_shell, bg=color, height=6).pack(fill="x")
            card = ttk.Frame(card_shell, style="Card.TFrame", padding=18)
            card.pack(side="left", expand=True, fill="both", padx=(0, 10))
            ttk.Label(card, text=title.upper(), style="StatCaption.TLabel").pack(anchor="w")
            value = ttk.Label(card, text="0", style="StatValue.TLabel")
            value.pack(anchor="w", pady=(10, 0))
            ttk.Label(card, text="Indicador consolidado", style="StatCaption.TLabel").pack(anchor="w", pady=(6, 0))
            self.stats_labels[title.lower()] = value

        self.section_title = ttk.Label(self, text="Dashboard", style="Title.TLabel")
        self.section_title.pack(anchor="w", pady=(0, 12))
        self._render_session_security_banner()

        scroll_shell = ttk.Frame(self, style="App.TFrame")
        scroll_shell.pack(fill="both", expand=True)

        self.scroll_canvas = tk.Canvas(
            scroll_shell,
            bg="#EEF3F8",
            highlightthickness=0,
            bd=0,
        )
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(
            scroll_shell,
            orient="vertical",
            command=self.scroll_canvas.yview,
        )
        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.content = ttk.Frame(self.scroll_canvas, style="Panel.TFrame", padding=20)
        self.content_window = self.scroll_canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw",
        )
        self.content.bind(
            "<Configure>",
            lambda _event: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")),
        )
        self.scroll_canvas.bind("<Configure>", self._resize_scroll_content)
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.refresh_all()
        self.show_section("dashboard")
        self._schedule_security_poll()

    def _render_session_security_banner(self) -> None:
        if not getattr(self.session, "security_alert_message", ""):
            if self.security_banner and self.security_banner.winfo_exists():
                self.security_banner.destroy()
                self.security_banner = None
            return

        if self.security_banner and self.security_banner.winfo_exists():
            self.security_banner.destroy()

        alert = tk.Frame(self, bg="#FFF5F5", highlightbackground="#C53B3B", highlightthickness=2)
        alert.pack(fill="x", pady=(0, 16), before=self.section_title)
        self.security_banner = alert
        accent = tk.Frame(alert, bg="#C53B3B", width=10)
        accent.pack(side="left", fill="y")
        body = tk.Frame(alert, bg="#FFF5F5")
        body.pack(side="left", fill="both", expand=True, padx=18, pady=16)
        tk.Label(
            body,
            text="ALERTA DE SEGURIDAD",
            bg="#FFF5F5",
            fg="#9B1C1C",
            font=("Segoe UI Semibold", 17),
        ).pack(anchor="w")
        tk.Label(
            body,
            text=self.session.security_alert_message,
            bg="#FFF5F5",
            fg="#9B1C1C",
            font=("Segoe UI", 11),
            wraplength=980,
            justify="left",
        ).pack(anchor="w", pady=(6, 0))

    def _schedule_security_poll(self) -> None:
        if self.winfo_exists():
            self._security_poll_job = self.after(self.SECURITY_POLL_MS, self._poll_security_state)

    def _poll_security_state(self) -> None:
        self._security_poll_job = None
        if not self.winfo_exists():
            return

        try:
            user_data = self.services["users"].get_user(self.session.user_id)
        except Exception:
            self._schedule_security_poll()
            return

        if user_data:
            alert_active = bool(user_data.get("security_alert_active", False))
            alert_message = user_data.get("security_alert_message", "") or ""
            status = (user_data.get("status") or "").lower()
            self.session.security_alert_active = alert_active
            self.session.security_alert_message = alert_message
            self.session.must_change_password = bool(user_data.get("must_change_password", self.session.must_change_password))

            if alert_active:
                self._render_session_security_banner()
                if not self._security_alert_seen:
                    self._show_security_lock_modal(alert_message)
            else:
                self._render_session_security_banner()

            self._security_alert_seen = alert_active
            if status == "bloqueado" and alert_active and not self._security_logout_in_progress:
                self._show_security_lock_modal(alert_message)

        self._schedule_security_poll()

    def destroy(self) -> None:
        if self._security_poll_job is not None:
            try:
                self.after_cancel(self._security_poll_job)
            except Exception:
                pass
            self._security_poll_job = None
        super().destroy()

    def _show_security_lock_modal(self, alert_message: str) -> None:
        if self._security_logout_in_progress or not self.winfo_exists():
            return

        self._security_logout_in_progress = True
        seconds_left = {"value": 10}
        modal = tk.Toplevel(self)
        modal.title("Alerta de seguridad")
        modal.transient(self.winfo_toplevel())
        modal.grab_set()
        modal.configure(bg="#7F1D1D")
        modal.geometry("620x280")
        modal.resizable(False, False)

        shell = tk.Frame(modal, bg="#FFF5F5", highlightbackground="#C53B3B", highlightthickness=3)
        shell.pack(fill="both", expand=True, padx=14, pady=14)
        tk.Label(
            shell,
            text="ALERTA DE SEGURIDAD",
            bg="#FFF5F5",
            fg="#9B1C1C",
            font=("Segoe UI Semibold", 22),
        ).pack(anchor="w", padx=22, pady=(22, 8))
        tk.Label(
            shell,
            text=alert_message,
            bg="#FFF5F5",
            fg="#9B1C1C",
            font=("Segoe UI", 12),
            wraplength=540,
            justify="left",
        ).pack(anchor="w", padx=22)
        countdown_var = tk.StringVar(value="Tu sesion se cerrara en 10 segundos.")
        tk.Label(
            shell,
            textvariable=countdown_var,
            bg="#FFF5F5",
            fg="#7F1D1D",
            font=("Segoe UI Semibold", 16),
        ).pack(anchor="w", padx=22, pady=(18, 8))
        tk.Label(
            shell,
            text="La cuenta fue bloqueada por seguridad y se cerrara esta sesion.",
            bg="#FFF5F5",
            fg="#B45309",
            font=("Segoe UI", 11),
        ).pack(anchor="w", padx=22)

        def tick() -> None:
            if not modal.winfo_exists():
                return
            if winsound:
                try:
                    winsound.MessageBeep(winsound.MB_ICONHAND)
                except Exception:
                    pass
            seconds_left["value"] -= 1
            if seconds_left["value"] <= 0:
                try:
                    modal.grab_release()
                except Exception:
                    pass
                modal.destroy()
                self.on_forced_logout()
                return
            countdown_var.set(f"Tu sesion se cerrara en {seconds_left['value']} segundos.")
            modal.after(1000, tick)

        modal.protocol("WM_DELETE_WINDOW", lambda: None)
        if winsound:
            try:
                winsound.MessageBeep(winsound.MB_ICONHAND)
            except Exception:
                pass
        modal.after(1000, tick)

    def _resize_scroll_content(self, event) -> None:
        self.scroll_canvas.itemconfigure(self.content_window, width=event.width)

    def _on_mousewheel(self, event) -> None:
        if self.winfo_exists():
            self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _assert_admin(self) -> bool:
        if self.session.role != "Administrador":
            messagebox.showwarning("SecureDesk", "Esta accion requiere permisos de Administrador.")
            return False
        return True

    def refresh_all(self) -> None:
        self.users = self.services["users"].list_users()
        self.tasks = self.services["tasks"].list_tasks()
        self.documents = self.services["documents"].list_documents()
        self.audit = self.services["audit"].list_events()
        self.task_lookup = {task["id"]: task.get("title", "") for task in self.tasks}
        if "usuarios" in self.stats_labels:
            self.stats_labels["usuarios"].configure(text=str(len(self.users)))
        self.stats_labels["tareas"].configure(text=str(len(self.tasks)))
        self.stats_labels["documentos"].configure(text=str(len(self.documents)))
        if "auditoria" in self.stats_labels:
            self.stats_labels["auditoria"].configure(text=str(len(self.audit)))

    def _task_name(self, task_id: str) -> str:
        if not task_id:
            return "Sin tarea vinculada"
        return self.task_lookup.get(task_id, task_id)

    def _set_control_feedback(self, control: dict, valid: bool, message: str) -> None:
        widget = control["widget"]
        feedback = control["feedback"]
        widget_type = control["type"]
        if widget_type == "combobox":
            widget.configure(style="Valid.TCombobox" if valid else "Invalid.TCombobox")
        elif widget_type == "entry":
            widget.configure(style="Valid.TEntry" if valid else "Invalid.TEntry")
        elif widget_type == "signature":
            widget.configure(
                highlightbackground="#2F855A" if valid else "#C53B3B",
                highlightthickness=1,
            )
        feedback.configure(
            text=message,
            style="SuccessFeedback.TLabel" if valid else "ErrorFeedback.TLabel",
        )

    def _value(self, control: dict) -> str:
        return control["var"].get().strip()

    def _validate_user_form(self, controls: dict, paint: bool = True) -> bool:
        results = {
            "username": (
                bool(self._value(controls["username"])) and bool(self.USERNAME_RE.fullmatch(self._value(controls["username"]))),
                "Usuario valido." if bool(self._value(controls["username"])) and bool(self.USERNAME_RE.fullmatch(self._value(controls["username"]))) else "4-30 caracteres: letras, numeros, punto, guion o guion bajo.",
            ),
            "full_name": (
                len(self._value(controls["full_name"])) >= 5,
                "Nombre correcto." if len(self._value(controls["full_name"])) >= 5 else "Ingresa nombre y apellido.",
            ),
            "email": (
                validate_email(self._value(controls["email"])),
                "Correo valido." if validate_email(self._value(controls["email"])) else "Correo electronico invalido.",
            ),
            "role": (
                self._value(controls["role"]) in self.user_roles,
                "Rol seleccionado." if self._value(controls["role"]) in self.user_roles else "Selecciona un rol.",
            ),
        }
        if paint:
            for key, (valid, message) in results.items():
                if key in controls:
                    self._set_control_feedback(controls[key], valid, message)
        return all(valid for valid, _ in results.values())

    def _validate_task_form(self, controls: dict, paint: bool = True) -> bool:
        results = {
            "title": (
                len(self._value(controls["title"])) >= 4,
                "Titulo valido." if len(self._value(controls["title"])) >= 4 else "Ingresa un titulo mas descriptivo.",
            ),
            "description": (
                len(self._value(controls["description"])) >= 8,
                "Descripcion valida." if len(self._value(controls["description"])) >= 8 else "Describe mejor la tarea.",
            ),
            "priority": (
                self._value(controls["priority"]) in self.task_priorities,
                "Prioridad seleccionada." if self._value(controls["priority"]) in self.task_priorities else "Selecciona una prioridad.",
            ),
            "status": (
                self._value(controls["status"]) in self.task_statuses,
                "Estado seleccionado." if self._value(controls["status"]) in self.task_statuses else "Selecciona un estado.",
            ),
            "due_date": (
                self._value(controls["due_date"]) in self.task_due_dates,
                "Fecha valida." if self._value(controls["due_date"]) in self.task_due_dates else "Selecciona una fecha valida.",
            ),
            "assigned_to": (
                bool(self._value(controls["assigned_to"])),
                "Responsable seleccionado." if bool(self._value(controls["assigned_to"])) else "Selecciona un responsable.",
            ),
        }
        if paint:
            for key, (valid, message) in results.items():
                self._set_control_feedback(controls[key], valid, message)
        return all(valid for valid, _ in results.values())

    def _validate_document_form(self, controls: dict, paint: bool = True) -> bool:
        file_ok = bool(self._value(controls["file_path"]))
        signature_name = self._value(controls["user_signature_name"])
        signature_control = controls.get("signature_pad")
        signature_drawn = signature_control["widget"].has_signature() if signature_control else False
        results = {
            "title": (
                len(self._value(controls["title"])) >= 4,
                "Titulo valido." if len(self._value(controls["title"])) >= 4 else "Ingresa un titulo para el documento.",
            ),
            "notes": (
                len(self._value(controls["notes"])) >= 4,
                "Notas validas." if len(self._value(controls["notes"])) >= 4 else "Agrega una nota breve.",
            ),
            "category": (
                self._value(controls["category"]) in self.document_categories,
                "Categoria seleccionada." if self._value(controls["category"]) in self.document_categories else "Selecciona una categoria.",
            ),
            "related_task_id": (
                bool(self._value(controls["related_task_id"])),
                "Relacion definida." if bool(self._value(controls["related_task_id"])) else "Selecciona una opcion.",
            ),
            "file_path": (
                file_ok,
                "Archivo seleccionado." if file_ok else "Selecciona un archivo.",
            ),
            "user_signature_name": (
                len(signature_name) >= 5,
                "Firmante identificado." if len(signature_name) >= 5 else "Captura el nombre del firmante.",
            ),
            "signature_pad": (
                signature_drawn,
                "Firma manuscrita capturada." if signature_drawn else "Firma en el recuadro con el mouse.",
            ),
        }
        if paint:
            for key, (valid, message) in results.items():
                if key in controls:
                    self._set_control_feedback(controls[key], valid, message)
        return all(valid for valid, _ in results.values())

    def show_section(self, section: str) -> None:
        self.current_section = section
        self.refresh_all()
        for child in self.content.winfo_children():
            child.destroy()
        self.scroll_canvas.yview_moveto(0)
        self.section_title.configure(text=section.capitalize())

        if section == "dashboard":
            self._render_dashboard_summary()
        elif section == "usuarios":
            self._render_users()
        elif section == "tareas":
            self._render_tasks()
        elif section == "documentos":
            self._render_documents()
        elif section == "auditoria":
            self._render_audit()

    def _tree(self, parent, columns, headings):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=14)
        for column, heading in zip(columns, headings):
            tree.heading(column, text=heading)
            tree.column(column, width=150, anchor="w")
        tree.pack(fill="both", expand=True, pady=(14, 0))
        return tree

    def _combo(self, parent, values, width=18, textvariable=None):
        combo = ttk.Combobox(parent, values=values, state="readonly", width=width, textvariable=textvariable)
        if values:
            combo.set(values[0])
        return combo

    def _render_responsive_fields(self, parent, field_specs, validator, max_columns=3):
        grid = ttk.Frame(parent, style="Panel.TFrame")
        grid.pack(fill="x", pady=(0, 12))
        for column in range(max_columns):
            grid.columnconfigure(column, weight=1)

        controls = {}
        for index, spec in enumerate(field_specs):
            row = (index // max_columns) * 3
            col = index % max_columns
            ttk.Label(grid, text=spec["label"], style="PanelText.TLabel").grid(
                row=row, column=col, sticky="w", padx=6
            )

            var = spec.get("variable") or tk.StringVar()
            if spec["kind"] == "combobox":
                widget = self._combo(grid, spec["values"], width=spec.get("width", 18), textvariable=var)
                widget.bind("<<ComboboxSelected>>", lambda _event, fn=validator, data=controls: fn(data, True))
                control_type = "combobox"
            else:
                widget = ttk.Entry(grid, textvariable=var, show=spec.get("show", ""))
                var.trace_add("write", lambda *_args, fn=validator, data=controls: fn(data, True))
                control_type = "entry"

            widget.grid(row=row + 1, column=col, sticky="ew", padx=6, pady=(4, 2))
            feedback = ttk.Label(grid, text=" ", style="PanelText.TLabel")
            feedback.grid(row=row + 2, column=col, sticky="w", padx=6, pady=(0, 10))

            controls[spec["key"]] = {
                "widget": widget,
                "var": var,
                "feedback": feedback,
                "type": control_type,
            }

        validator(controls, True)
        return controls

    def _render_dashboard_summary(self) -> None:
        if self.session.role == "Administrador":
            summary = ttk.Frame(self.content, style="Card.TFrame")
            summary.pack(fill="both", expand=True, pady=(16, 0))

            left_shell = tk.Frame(summary, bg="#FFFFFF", highlightbackground="#D5DFEA", highlightthickness=1)
            left_shell.pack(side="left", fill="both", expand=True, padx=(0, 12))
            tk.Frame(left_shell, bg="#1E5AA8", height=5).pack(fill="x")
            left = ttk.Frame(left_shell, style="Card.TFrame", padding=18)
            left.pack(side="left", fill="both", expand=True, padx=(0, 12))
            right_shell = tk.Frame(summary, bg="#FFFFFF", highlightbackground="#D5DFEA", highlightthickness=1)
            right_shell.pack(side="left", fill="both", expand=True)
            tk.Frame(right_shell, bg="#C18A2C", height=5).pack(fill="x")
            right = ttk.Frame(right_shell, style="Card.TFrame", padding=18)
            right.pack(side="left", fill="both", expand=True)

            ttk.Label(left, text="Tareas recientes", style="PanelTitle.TLabel").pack(anchor="w")
            ttk.Label(left, text="Seguimiento de actividad operativa actual", style="PanelText.TLabel").pack(anchor="w", pady=(4, 0))
            task_tree = self._tree(left, ("title", "priority", "status"), ("Titulo", "Prioridad", "Estado"))
            for item in self.tasks[-8:]:
                task_tree.insert("", "end", values=(item.get("title"), item.get("priority"), item.get("status")))

            ttk.Label(right, text="Eventos criticos", style="PanelTitle.TLabel").pack(anchor="w")
            ttk.Label(right, text="Alertas y movimientos relevantes de seguridad", style="PanelText.TLabel").pack(anchor="w", pady=(4, 0))
            audit_tree = self._tree(right, ("type", "actor", "description"), ("Evento", "Actor", "Descripcion"))
            for item in self.audit[:8]:
                audit_tree.insert("", "end", values=(item.get("event_type"), item.get("actor"), item.get("description")))
            return

        summary = ttk.Frame(self.content, style="Card.TFrame")
        summary.pack(fill="both", expand=True, pady=(16, 0))

        left_shell = tk.Frame(summary, bg="#FFFFFF", highlightbackground="#D5DFEA", highlightthickness=1)
        left_shell.pack(side="left", fill="both", expand=True, padx=(0, 12))
        tk.Frame(left_shell, bg="#1E5AA8", height=5).pack(fill="x")
        left = ttk.Frame(left_shell, style="Card.TFrame", padding=18)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right_shell = tk.Frame(summary, bg="#FFFFFF", highlightbackground="#D5DFEA", highlightthickness=1)
        right_shell.pack(side="left", fill="both", expand=True)
        tk.Frame(right_shell, bg="#0F766E", height=5).pack(fill="x")
        right = ttk.Frame(right_shell, style="Card.TFrame", padding=18)
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="Mis tareas recientes", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(left, text="Prioridades y estatus recientes de ejecucion", style="PanelText.TLabel").pack(anchor="w", pady=(4, 0))
        task_tree = self._tree(left, ("title", "priority", "status"), ("Titulo", "Prioridad", "Estado"))
        for item in self.tasks[-8:]:
            task_tree.insert("", "end", values=(item.get("title"), item.get("priority"), item.get("status")))

        ttk.Label(right, text="Documentos recientes", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(right, text="Documentos vinculados a tus operaciones recientes", style="PanelText.TLabel").pack(anchor="w", pady=(4, 0))
        doc_tree = self._tree(right, ("title", "category", "task"), ("Titulo", "Categoria", "Tarea"))
        for item in self.documents[-8:]:
            doc_tree.insert("", "end", values=(item.get("title"), item.get("category"), self._task_name(item.get("related_task_id", ""))))

    def _render_users(self) -> None:
        top = ttk.Frame(self.content, style="Card.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text="Administracion de usuarios", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(
            top,
            text="Solo el administrador crea cuentas. La contrasena provisional se genera automaticamente y se envia al correo del usuario.",
            style="PanelText.TLabel",
        ).pack(anchor="w", pady=(4, 12))

        field_specs = [
            {"label": "Usuario", "key": "username", "kind": "entry"},
            {"label": "Nombre completo", "key": "full_name", "kind": "entry"},
            {"label": "Correo", "key": "email", "kind": "entry"},
            {"label": "Rol", "key": "role", "kind": "combobox", "values": self.user_roles, "width": 16},
        ]
        entries = self._render_responsive_fields(self.content, field_specs, self._validate_user_form, max_columns=3)

        ttk.Button(
            self.content,
            text="Crear usuario",
            style="Primary.TButton",
            command=lambda: self._create_user(entries),
        ).pack(anchor="e", pady=(0, 10))

        tree = self._tree(
            self.content,
            ("username", "name", "email", "role", "status"),
            ("Usuario", "Nombre", "Correo", "Rol", "Estado"),
        )
        for item in self.users:
            tags = ()
            if item.get("status") == "bloqueado" or item.get("security_alert_active"):
                tags = ("security_blocked",)
            tree.insert("", "end", iid=item["id"], values=(item.get("username"), item.get("full_name"), item.get("email"), item.get("role"), item.get("status")), tags=tags)
        tree.tag_configure("security_blocked", background="#FFF5F5", foreground="#9B1C1C")

        actions = ttk.Frame(self.content, style="Panel.TFrame")
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Bloquear seleccionado", style="Secondary.TButton", command=lambda: self._update_user_status(tree, "bloqueado")).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Activar seleccionado", style="Secondary.TButton", command=lambda: self._update_user_status(tree, "activo")).pack(side="left")
        ttk.Button(actions, text="Quitar bloqueo", style="Secondary.TButton", command=lambda: self._clear_security_lock(tree)).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Simular ataque", style="Primary.TButton", command=lambda: self._simulate_security_incident(tree)).pack(side="right")

    def _render_tasks(self) -> None:
        ttk.Label(self.content, text="Gestion de tareas", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(self.content, text="Usa opciones predefinidas para prioridad, estado, fecha y responsable.", style="PanelText.TLabel").pack(anchor="w", pady=(4, 12))

        assignee_options = [
            user.get("username")
            for user in self.users
            if user.get("role") != "Administrador"
        ] or ["Sin asignar"]
        field_specs = [
            {"label": "Titulo", "key": "title", "kind": "entry"},
            {"label": "Descripcion", "key": "description", "kind": "entry"},
            {"label": "Prioridad", "key": "priority", "kind": "combobox", "values": self.task_priorities, "width": 16},
            {"label": "Estado", "key": "status", "kind": "combobox", "values": self.task_statuses, "width": 16},
            {"label": "Fecha limite", "key": "due_date", "kind": "combobox", "values": self.task_due_dates, "width": 16},
            {"label": "Asignado a", "key": "assigned_to", "kind": "combobox", "values": assignee_options, "width": 16},
        ]
        entries = self._render_responsive_fields(self.content, field_specs, self._validate_task_form, max_columns=3)

        ttk.Button(
            self.content,
            text="Crear tarea",
            style="Primary.TButton",
            command=lambda: self._create_task(entries),
        ).pack(anchor="e", pady=(0, 10))

        tree = self._tree(self.content, ("title", "priority", "status", "due", "assigned"), ("Titulo", "Prioridad", "Estado", "Fecha limite", "Asignado"))
        for item in self.tasks:
            tree.insert("", "end", iid=item["id"], values=(item.get("title"), item.get("priority"), item.get("status"), item.get("due_date"), item.get("assigned_to")))

        actions = ttk.Frame(self.content, style="Panel.TFrame")
        actions.pack(fill="x", pady=(0, 10))
        ttk.Button(actions, text="Marcar en progreso", style="Secondary.TButton", command=lambda: self._update_task_status(tree, "En progreso")).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Marcar completada", style="Secondary.TButton", command=lambda: self._update_task_status(tree, "Completada")).pack(side="left")
        ttk.Button(actions, text="Marcar bloqueada", style="Secondary.TButton", command=lambda: self._update_task_status(tree, "Bloqueada")).pack(side="left", padx=(8, 0))

    def _render_documents(self) -> None:
        ttk.Label(self.content, text="Gestion documental", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(self.content, text="Las categorias y tareas relacionadas se eligen desde listas predefinidas.", style="PanelText.TLabel").pack(anchor="w", pady=(4, 12))

        task_options = [("Sin tarea vinculada", "")]
        task_options.extend([(task.get("title", task["id"]), task["id"]) for task in self.tasks])
        task_labels = [label for label, _ in task_options]

        field_specs = [
            {"label": "Titulo", "key": "title", "kind": "entry"},
            {"label": "Notas", "key": "notes", "kind": "entry"},
            {"label": "Categoria", "key": "category", "kind": "combobox", "values": self.document_categories, "width": 18},
            {"label": "Tarea relacionada", "key": "related_task_id", "kind": "combobox", "values": task_labels, "width": 22},
            {"label": "Archivo", "key": "file_path", "kind": "entry", "variable": self.file_path_var},
            {"label": "Nombre del firmante", "key": "user_signature_name", "kind": "entry", "variable": tk.StringVar(value=self.session.full_name)},
        ]
        entries = self._render_responsive_fields(self.content, field_specs, self._validate_document_form, max_columns=3)

        signature_shell = ttk.Frame(self.content, style="Card.TFrame")
        signature_shell.pack(fill="x", pady=(0, 12))
        ttk.Label(signature_shell, text="Firma manuscrita", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(signature_shell, text="Dibuja la firma con el mouse dentro del recuadro.", style="PanelText.TLabel").pack(anchor="w", pady=(4, 10))

        signature_pad = SignaturePad(
            signature_shell,
            width=520,
            height=170,
            on_change=lambda: self._validate_document_form(entries, True),
        )
        signature_pad.pack(anchor="w", fill="x")
        pad_feedback = ttk.Label(signature_shell, text="Firma en el recuadro con el mouse.", style="ErrorFeedback.TLabel")
        pad_feedback.pack(anchor="w", pady=(8, 6))
        clear_actions = ttk.Frame(signature_shell, style="Card.TFrame")
        clear_actions.pack(fill="x")
        ttk.Button(
            clear_actions,
            text="Limpiar firma",
            style="Secondary.TButton",
            command=lambda: self._clear_signature(entries),
        ).pack(anchor="w")

        entries["signature_pad"] = {
            "widget": signature_pad,
            "var": tk.StringVar(),
            "feedback": pad_feedback,
            "type": "signature",
        }
        self._validate_document_form(entries, True)

        actions = ttk.Frame(self.content, style="Panel.TFrame")
        actions.pack(fill="x", pady=(0, 10))
        ttk.Button(actions, text="Buscar archivo", style="Secondary.TButton", command=lambda: self._select_file(entries)).pack(side="left")
        ttk.Button(actions, text="Registrar documento", style="Primary.TButton", command=lambda: self._create_document(entries, task_options)).pack(side="right")

        tree = self._tree(self.content, ("title", "category", "task", "hash", "signature", "user_sign"), ("Titulo", "Categoria", "Tarea", "Hash", "Firma sistema", "Firmante"))
        for item in self.documents:
            signature_preview = "Firmado" if item.get("digital_signature") else "Pendiente"
            tree.insert("", "end", values=(item.get("title"), item.get("category"), self._task_name(item.get("related_task_id", "")), (item.get("integrity_hash") or "")[:18], signature_preview, item.get("user_signature_name", "")))

    def _render_audit(self) -> None:
        ttk.Label(self.content, text="Registro de auditoria", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(self.content, text="Eventos de seguridad y operaciones relevantes del sistema.", style="PanelText.TLabel").pack(anchor="w", pady=(4, 12))
        tree = self._tree(self.content, ("type", "actor", "description", "created"), ("Evento", "Actor", "Descripcion", "Fecha"))
        for item in self.audit:
            created = item.get("created_at")
            event_type = item.get("event_type", "")
            tags = ()
            if "security" in event_type.lower() or "bruteforce" in event_type.lower():
                tags = ("security",)
            tree.insert("", "end", values=(event_type, item.get("actor"), item.get("description"), created.strftime("%Y-%m-%d %H:%M") if created else ""), tags=tags)
        tree.tag_configure("security", background="#FFF5F5", foreground="#9B1C1C")

    def _create_user(self, entries) -> None:
        if not self._assert_admin():
            return
        if not self._validate_user_form(entries, True):
            messagebox.showwarning("SecureDesk", "Corrige los campos marcados antes de guardar.")
            return
        try:
            self.services["users"].create_user(
                self.session.username,
                self._value(entries["username"]),
                self._value(entries["full_name"]),
                self._value(entries["email"]),
                self._value(entries["role"]),
            )
            messagebox.showinfo("SecureDesk", "Usuario creado correctamente. La contrasena provisional fue enviada por correo.")
            self.show_section("usuarios")
        except Exception as exc:
            messagebox.showerror("SecureDesk", str(exc))

    def _update_user_status(self, tree, status: str) -> None:
        if not self._assert_admin():
            return
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("SecureDesk", "Selecciona un usuario.")
            return
        try:
            self.services["users"].update_status(self.session.username, selection[0], status)
            messagebox.showinfo("SecureDesk", "Estado actualizado.")
            self.show_section("usuarios")
        except Exception as exc:
            messagebox.showerror("SecureDesk", str(exc))

    def _simulate_security_incident(self, tree) -> None:
        if not self._assert_admin():
            return
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("SecureDesk", "Selecciona un usuario para simular el incidente.")
            return
        user = next((item for item in self.users if item.get("id") == selection[0]), None)
        if not user:
            messagebox.showwarning("SecureDesk", "No se encontro el usuario seleccionado.")
            return
        if not messagebox.askyesno(
            "SecureDesk",
            f"Se simulara un intento de fuerza bruta defensivo sobre {user.get('username')}. "
            "Esto bloqueara temporalmente la cuenta y enviara alertas. Deseas continuar?",
        ):
            return
        try:
            self.services["security"].trigger_simulated_bruteforce(user.get("username", ""))
            messagebox.showinfo(
                "SecureDesk",
                "Incidente simulado correctamente. La cuenta fue bloqueada y se enviaron las alertas configuradas.",
            )
            self.show_section("usuarios")
        except Exception as exc:
            messagebox.showerror("SecureDesk", str(exc))

    def _clear_security_lock(self, tree) -> None:
        if not self._assert_admin():
            return
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("SecureDesk", "Selecciona un usuario.")
            return
        try:
            self.services["users"].clear_security_lock(self.session.username, selection[0])
            messagebox.showinfo("SecureDesk", "Bloqueo de seguridad retirado.")
            self.show_section("usuarios")
        except Exception as exc:
            messagebox.showerror("SecureDesk", str(exc))

    def _create_task(self, entries) -> None:
        if not self._validate_task_form(entries, True):
            messagebox.showwarning("SecureDesk", "Corrige los campos marcados antes de guardar.")
            return
        try:
            self.services["tasks"].create_task(
                self.session.username,
                self._value(entries["title"]),
                self._value(entries["description"]),
                self._value(entries["priority"]),
                self._value(entries["status"]),
                "" if self._value(entries["due_date"]) == "Sin fecha" else self._value(entries["due_date"]),
                self._value(entries["assigned_to"]),
            )
            messagebox.showinfo("SecureDesk", "Tarea creada correctamente.")
            self.show_section("tareas")
        except Exception as exc:
            messagebox.showerror("SecureDesk", str(exc))

    def _update_task_status(self, tree, status: str) -> None:
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("SecureDesk", "Selecciona una tarea.")
            return
        try:
            self.services["tasks"].update_task_status(self.session.username, selection[0], status)
            messagebox.showinfo("SecureDesk", "Estado de tarea actualizado.")
            self.show_section("tareas")
        except Exception as exc:
            messagebox.showerror("SecureDesk", str(exc))

    def _select_file(self, entries) -> None:
        path = filedialog.askopenfilename(title="Seleccionar documento")
        if path:
            self.file_path_var.set(path)
            self._validate_document_form(entries, True)

    def _clear_signature(self, entries) -> None:
        entries["signature_pad"]["widget"].clear()
        self._validate_document_form(entries, True)

    def _create_document(self, entries, task_options) -> None:
        if not self._validate_document_form(entries, True):
            messagebox.showwarning("SecureDesk", "Corrige los campos marcados antes de guardar.")
            return
        try:
            selected_label = self._value(entries["related_task_id"])
            selected_task_id = ""
            for label, task_id in task_options:
                if label == selected_label:
                    selected_task_id = task_id
                    break
            self.services["documents"].register_document(
                self.session.username,
                self._value(entries["title"]),
                self._value(entries["category"]),
                selected_task_id,
                self._value(entries["file_path"]),
                self._value(entries["notes"]),
                self._value(entries["user_signature_name"]),
                entries["signature_pad"]["widget"].export_svg(),
            )
            messagebox.showinfo("SecureDesk", "Documento registrado correctamente.")
            self.file_path_var.set("")
            self.show_section("documentos")
        except Exception as exc:
            messagebox.showerror("SecureDesk", str(exc))
