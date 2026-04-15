from __future__ import annotations

from datetime import date, timedelta
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.core.security import validate_email


class DashboardView(ttk.Frame):
    USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{4,30}$")

    def __init__(self, parent, services, session) -> None:
        super().__init__(parent, style="App.TFrame", padding=24)
        self.services = services
        self.session = session
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
            text=f"Sesion activa: {self.session.full_name} ({self.session.role})",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        stats = ttk.Frame(self, style="App.TFrame")
        stats.pack(fill="x", pady=(0, 20))
        card_titles = ["Tareas", "Documentos"]
        if self.session.role == "Administrador":
            card_titles = ["Usuarios", "Tareas", "Documentos", "Auditoria"]
        self.stats_labels = {}
        for title in card_titles:
            card = ttk.Frame(stats, style="Panel.TFrame", padding=18)
            card.pack(side="left", expand=True, fill="both", padx=(0, 10))
            ttk.Label(card, text=title, style="PanelText.TLabel").pack(anchor="w")
            value = ttk.Label(card, text="0", style="PanelTitle.TLabel")
            value.pack(anchor="w", pady=(8, 0))
            self.stats_labels[title.lower()] = value

        self.section_title = ttk.Label(self, text="Dashboard", style="Title.TLabel")
        self.section_title.pack(anchor="w", pady=(0, 12))

        self.content = ttk.Frame(self, style="Panel.TFrame", padding=20)
        self.content.pack(fill="both", expand=True)

        self.refresh_all()
        self.show_section("dashboard")

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

    def _password_message(self, password: str) -> tuple[bool, str]:
        if len(password) < 8:
            return False, "Minimo 8 caracteres."
        if not any(char.isupper() for char in password):
            return False, "Incluye una mayuscula."
        if not any(char.islower() for char in password):
            return False, "Incluye una minuscula."
        if not any(char.isdigit() for char in password):
            return False, "Incluye un numero."
        if not any(char in "!@#$%^&*()-_=+[]{};:,.?" for char in password):
            return False, "Incluye un simbolo."
        return True, "Contrasena valida."

    def _set_control_feedback(self, control: dict, valid: bool, message: str) -> None:
        widget = control["widget"]
        feedback = control["feedback"]
        widget_type = control["type"]
        if widget_type == "combobox":
            widget.configure(style="Valid.TCombobox" if valid else "Invalid.TCombobox")
        else:
            widget.configure(style="Valid.TEntry" if valid else "Invalid.TEntry")
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
        password_ok, password_msg = self._password_message(self._value(controls["password"]))
        results["password"] = (password_ok, password_msg)
        if paint:
            for key, (valid, message) in results.items():
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
        }
        if paint:
            for key, (valid, message) in results.items():
                self._set_control_feedback(controls[key], valid, message)
        return all(valid for valid, _ in results.values())

    def show_section(self, section: str) -> None:
        self.current_section = section
        self.refresh_all()
        for child in self.content.winfo_children():
            child.destroy()
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
            ttk.Label(
                self.content,
                text="Resumen ejecutivo con tareas recientes y eventos criticos de auditoria.",
                style="PanelText.TLabel",
            ).pack(anchor="w")

            summary = ttk.Frame(self.content, style="Panel.TFrame")
            summary.pack(fill="both", expand=True, pady=(16, 0))

            left = ttk.Frame(summary, style="Panel.TFrame")
            left.pack(side="left", fill="both", expand=True, padx=(0, 12))
            right = ttk.Frame(summary, style="Panel.TFrame")
            right.pack(side="left", fill="both", expand=True)

            ttk.Label(left, text="Tareas recientes", style="PanelTitle.TLabel").pack(anchor="w")
            task_tree = self._tree(left, ("title", "priority", "status"), ("Titulo", "Prioridad", "Estado"))
            for item in self.tasks[-8:]:
                task_tree.insert("", "end", values=(item.get("title"), item.get("priority"), item.get("status")))

            ttk.Label(right, text="Eventos criticos", style="PanelTitle.TLabel").pack(anchor="w")
            audit_tree = self._tree(right, ("type", "actor", "description"), ("Evento", "Actor", "Descripcion"))
            for item in self.audit[:8]:
                audit_tree.insert("", "end", values=(item.get("event_type"), item.get("actor"), item.get("description")))
            return

        ttk.Label(
            self.content,
            text="Resumen operativo del usuario sin exponer informacion de auditoria.",
            style="PanelText.TLabel",
        ).pack(anchor="w")

        summary = ttk.Frame(self.content, style="Panel.TFrame")
        summary.pack(fill="both", expand=True, pady=(16, 0))

        left = ttk.Frame(summary, style="Panel.TFrame")
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right = ttk.Frame(summary, style="Panel.TFrame")
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="Mis tareas recientes", style="PanelTitle.TLabel").pack(anchor="w")
        task_tree = self._tree(left, ("title", "priority", "status"), ("Titulo", "Prioridad", "Estado"))
        for item in self.tasks[-8:]:
            task_tree.insert("", "end", values=(item.get("title"), item.get("priority"), item.get("status")))

        ttk.Label(right, text="Documentos recientes", style="PanelTitle.TLabel").pack(anchor="w")
        doc_tree = self._tree(right, ("title", "category", "task"), ("Titulo", "Categoria", "Tarea"))
        for item in self.documents[-8:]:
            doc_tree.insert("", "end", values=(item.get("title"), item.get("category"), self._task_name(item.get("related_task_id", ""))))

    def _render_users(self) -> None:
        top = ttk.Frame(self.content, style="Panel.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text="Administracion de usuarios", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(
            top,
            text="Solo el administrador crea cuentas y define la contrasena provisional.",
            style="PanelText.TLabel",
        ).pack(anchor="w", pady=(4, 12))

        field_specs = [
            {"label": "Usuario", "key": "username", "kind": "entry"},
            {"label": "Nombre completo", "key": "full_name", "kind": "entry"},
            {"label": "Correo", "key": "email", "kind": "entry"},
            {"label": "Rol", "key": "role", "kind": "combobox", "values": self.user_roles, "width": 16},
            {"label": "Contrasena provisional", "key": "password", "kind": "entry", "show": "*"},
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
            tree.insert("", "end", iid=item["id"], values=(item.get("username"), item.get("full_name"), item.get("email"), item.get("role"), item.get("status")))

        actions = ttk.Frame(self.content, style="Panel.TFrame")
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Bloquear seleccionado", style="Secondary.TButton", command=lambda: self._update_user_status(tree, "bloqueado")).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Activar seleccionado", style="Secondary.TButton", command=lambda: self._update_user_status(tree, "activo")).pack(side="left")

    def _render_tasks(self) -> None:
        ttk.Label(self.content, text="Gestion de tareas", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(self.content, text="Usa opciones predefinidas para prioridad, estado, fecha y responsable.", style="PanelText.TLabel").pack(anchor="w", pady=(4, 12))

        assignee_options = [user.get("username") for user in self.users] or ["Sin asignar"]
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

        actions = ttk.Frame(self.content, style="Panel.TFrame")
        actions.pack(fill="x", pady=(0, 10))
        ttk.Button(actions, text="Marcar en progreso", style="Secondary.TButton", command=lambda: self._update_task_status(tree, "En progreso")).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Marcar completada", style="Secondary.TButton", command=lambda: self._update_task_status(tree, "Completada")).pack(side="left")
        ttk.Button(actions, text="Marcar bloqueada", style="Secondary.TButton", command=lambda: self._update_task_status(tree, "Bloqueada")).pack(side="left", padx=(8, 0))

        tree = self._tree(self.content, ("title", "priority", "status", "due", "assigned"), ("Titulo", "Prioridad", "Estado", "Fecha limite", "Asignado"))
        for item in self.tasks:
            tree.insert("", "end", iid=item["id"], values=(item.get("title"), item.get("priority"), item.get("status"), item.get("due_date"), item.get("assigned_to")))

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
        ]
        entries = self._render_responsive_fields(self.content, field_specs, self._validate_document_form, max_columns=3)

        actions = ttk.Frame(self.content, style="Panel.TFrame")
        actions.pack(fill="x", pady=(0, 10))
        ttk.Button(actions, text="Buscar archivo", style="Secondary.TButton", command=lambda: self._select_file(entries)).pack(side="left")
        ttk.Button(actions, text="Registrar documento", style="Primary.TButton", command=lambda: self._create_document(entries, task_options)).pack(side="right")

        tree = self._tree(self.content, ("title", "category", "task", "hash", "signature"), ("Titulo", "Categoria", "Tarea", "Hash", "Firma"))
        for item in self.documents:
            signature_preview = "Firmado" if item.get("digital_signature") else "Pendiente"
            tree.insert("", "end", values=(item.get("title"), item.get("category"), self._task_name(item.get("related_task_id", "")), (item.get("integrity_hash") or "")[:18], signature_preview))

    def _render_audit(self) -> None:
        ttk.Label(self.content, text="Registro de auditoria", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(self.content, text="Eventos de seguridad y operaciones relevantes del sistema.", style="PanelText.TLabel").pack(anchor="w", pady=(4, 12))
        tree = self._tree(self.content, ("type", "actor", "description", "created"), ("Evento", "Actor", "Descripcion", "Fecha"))
        for item in self.audit:
            created = item.get("created_at")
            tree.insert("", "end", values=(item.get("event_type"), item.get("actor"), item.get("description"), created.strftime("%Y-%m-%d %H:%M") if created else ""))

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
                self._value(entries["password"]),
            )
            messagebox.showinfo("SecureDesk", "Usuario creado correctamente.")
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
            )
            messagebox.showinfo("SecureDesk", "Documento registrado correctamente.")
            self.file_path_var.set("")
            self.show_section("documentos")
        except Exception as exc:
            messagebox.showerror("SecureDesk", str(exc))
