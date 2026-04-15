from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class DashboardView(ttk.Frame):
    def __init__(self, parent, services, session) -> None:
        super().__init__(parent, style="App.TFrame", padding=24)
        self.services = services
        self.session = session
        self.current_section = None
        self.file_path_var = tk.StringVar()
        self._build()

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
        if "usuarios" in self.stats_labels:
            self.stats_labels["usuarios"].configure(text=str(len(self.users)))
        self.stats_labels["tareas"].configure(text=str(len(self.tasks)))
        self.stats_labels["documentos"].configure(text=str(len(self.documents)))
        if "auditoria" in self.stats_labels:
            self.stats_labels["auditoria"].configure(text=str(len(self.audit)))

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
            doc_tree.insert("", "end", values=(item.get("title"), item.get("category"), item.get("related_task_id")))

    def _render_users(self) -> None:
        top = ttk.Frame(self.content, style="Panel.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text="Administracion de usuarios", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(
            top,
            text="Solo el administrador crea cuentas y define la contrasena provisional.",
            style="PanelText.TLabel",
        ).pack(anchor="w", pady=(4, 12))

        form = ttk.Frame(self.content, style="Panel.TFrame")
        form.pack(fill="x")

        entries = {}
        fields = [
            ("Usuario", "username"),
            ("Nombre completo", "full_name"),
            ("Correo", "email"),
            ("Rol", "role"),
            ("Contrasena provisional", "password"),
        ]
        for index, (label, key) in enumerate(fields):
            ttk.Label(form, text=label, style="PanelText.TLabel").grid(row=0, column=index, sticky="w", padx=4)
            show = "*" if key == "password" else ""
            entry = ttk.Entry(form, show=show)
            entry.grid(row=1, column=index, sticky="ew", padx=4, pady=(4, 10))
            entries[key] = entry
            form.columnconfigure(index, weight=1)

        ttk.Button(
            form,
            text="Crear usuario",
            style="Primary.TButton",
            command=lambda: self._create_user(entries),
        ).grid(row=1, column=len(fields), padx=(10, 0))

        tree = self._tree(
            self.content,
            ("username", "name", "email", "role", "status"),
            ("Usuario", "Nombre", "Correo", "Rol", "Estado"),
        )
        for item in self.users:
            tree.insert(
                "",
                "end",
                iid=item["id"],
                values=(item.get("username"), item.get("full_name"), item.get("email"), item.get("role"), item.get("status")),
            )

        actions = ttk.Frame(self.content, style="Panel.TFrame")
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(
            actions,
            text="Bloquear seleccionado",
            style="Secondary.TButton",
            command=lambda: self._update_user_status(tree, "bloqueado"),
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            actions,
            text="Activar seleccionado",
            style="Secondary.TButton",
            command=lambda: self._update_user_status(tree, "activo"),
        ).pack(side="left")

    def _render_tasks(self) -> None:
        ttk.Label(self.content, text="Gestion de tareas", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(self.content, text="Registro de tareas con prioridad, avance y fecha limite.", style="PanelText.TLabel").pack(anchor="w", pady=(4, 12))

        form = ttk.Frame(self.content, style="Panel.TFrame")
        form.pack(fill="x")
        entries = {}
        fields = [("Titulo", "title"), ("Descripcion", "description"), ("Prioridad", "priority"), ("Estado", "status"), ("Fecha limite", "due_date"), ("Asignado a", "assigned_to")]
        for index, (label, key) in enumerate(fields):
            ttk.Label(form, text=label, style="PanelText.TLabel").grid(row=0, column=index, sticky="w", padx=4)
            entry = ttk.Entry(form)
            entry.grid(row=1, column=index, sticky="ew", padx=4, pady=(4, 10))
            entries[key] = entry
            form.columnconfigure(index, weight=1)

        ttk.Button(form, text="Crear tarea", style="Primary.TButton", command=lambda: self._create_task(entries)).grid(row=1, column=len(fields), padx=(10, 0))

        tree = self._tree(self.content, ("title", "priority", "status", "due", "assigned"), ("Titulo", "Prioridad", "Estado", "Fecha limite", "Asignado"))
        for item in self.tasks:
            tree.insert("", "end", iid=item["id"], values=(item.get("title"), item.get("priority"), item.get("status"), item.get("due_date"), item.get("assigned_to")))

        actions = ttk.Frame(self.content, style="Panel.TFrame")
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Marcar en progreso", style="Secondary.TButton", command=lambda: self._update_task_status(tree, "En progreso")).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Marcar completada", style="Secondary.TButton", command=lambda: self._update_task_status(tree, "Completada")).pack(side="left")

    def _render_documents(self) -> None:
        ttk.Label(self.content, text="Gestion documental", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(self.content, text="Registro documental con hash de integridad y vinculo a tareas.", style="PanelText.TLabel").pack(anchor="w", pady=(4, 12))

        form = ttk.Frame(self.content, style="Panel.TFrame")
        form.pack(fill="x")
        entries = {}
        fields = [("Titulo", "title"), ("Categoria", "category"), ("ID tarea", "related_task_id"), ("Notas", "notes")]
        for index, (label, key) in enumerate(fields):
            ttk.Label(form, text=label, style="PanelText.TLabel").grid(row=0, column=index, sticky="w", padx=4)
            entry = ttk.Entry(form)
            entry.grid(row=1, column=index, sticky="ew", padx=4, pady=(4, 10))
            entries[key] = entry
            form.columnconfigure(index, weight=1)

        ttk.Label(form, text="Archivo", style="PanelText.TLabel").grid(row=0, column=len(fields), sticky="w", padx=4)
        ttk.Entry(form, textvariable=self.file_path_var).grid(row=1, column=len(fields), sticky="ew", padx=4, pady=(4, 10))
        form.columnconfigure(len(fields), weight=1)
        ttk.Button(form, text="Buscar archivo", style="Secondary.TButton", command=self._select_file).grid(row=1, column=len(fields) + 1, padx=(8, 0))
        ttk.Button(form, text="Registrar documento", style="Primary.TButton", command=lambda: self._create_document(entries)).grid(row=1, column=len(fields) + 2, padx=(8, 0))

        tree = self._tree(self.content, ("title", "category", "task", "hash"), ("Titulo", "Categoria", "Tarea", "Hash"))
        for item in self.documents:
            tree.insert("", "end", values=(item.get("title"), item.get("category"), item.get("related_task_id"), (item.get("integrity_hash") or "")[:18]))

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
        try:
            self.services["users"].create_user(self.session.username, entries["username"].get(), entries["full_name"].get(), entries["email"].get(), entries["role"].get(), entries["password"].get())
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
        try:
            self.services["tasks"].create_task(self.session.username, entries["title"].get(), entries["description"].get(), entries["priority"].get(), entries["status"].get(), entries["due_date"].get(), entries["assigned_to"].get())
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

    def _select_file(self) -> None:
        path = filedialog.askopenfilename(title="Seleccionar documento")
        if path:
            self.file_path_var.set(path)

    def _create_document(self, entries) -> None:
        try:
            self.services["documents"].register_document(self.session.username, entries["title"].get(), entries["category"].get(), entries["related_task_id"].get(), self.file_path_var.get(), entries["notes"].get())
            messagebox.showinfo("SecureDesk", "Documento registrado correctamente.")
            self.file_path_var.set("")
            self.show_section("documentos")
        except Exception as exc:
            messagebox.showerror("SecureDesk", str(exc))
