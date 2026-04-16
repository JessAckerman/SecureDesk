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
        self.show_password_var = tk.BooleanVar(value=False)
        self.privacy_var = BooleanVar(value=False)
        self.terms_var = BooleanVar(value=False)
        self.confidentiality_var = BooleanVar(value=False)
        self.message_var = StringVar(
            value="Debes cambiar la contrasena provisional y aceptar los avisos para activar tu cuenta."
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
        password_row = ttk.Frame(panel, style="Card.TFrame")
        password_row.pack(fill="x", pady=(4, 16))
        self.password_entry = ttk.Entry(password_row, textvariable=self.password_var, show="*", font=("Segoe UI", 11))
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.password_toggle = ttk.Button(
            password_row,
            text="Ver",
            style="Secondary.TButton",
            command=self._toggle_password_visibility,
            width=10,
        )
        self.password_toggle.pack(side="left", padx=(8, 0))
        self.password_feedback = ttk.Label(panel, text="Usa mayuscula, minuscula, numero y simbolo.", style="PanelText.TLabel")
        self.password_feedback.pack(anchor="w", pady=(0, 12))
        self.password_var.trace_add("write", lambda *_: self._validate_password())

        for title, summary, text, variable, label in [
            (
                "Terminos y Condiciones de Uso",
                "Regula el uso permitido del sistema, el acceso de usuarios, la seguridad de la informacion y las responsabilidades dentro de SecureDesk.",
                """Sistema: SecureDesk
Version: 1.0
Ultima actualizacion: 2026

1. Introduccion
Los presentes Terminos y Condiciones regulan el uso de la aplicacion SecureDesk, un sistema de gestion de tareas y documentos desarrollado para uso interno de organizaciones.
El uso de la aplicacion implica la aceptacion total de los presentes terminos por parte del usuario. En caso de no estar de acuerdo con alguna de las condiciones aqui establecidas, el usuario debera abstenerse de utilizar la aplicacion.

2. Definiciones
Sistema: Aplicacion SecureDesk utilizada para la gestion de tareas, documentos y usuarios dentro de una organizacion.
Usuario: Persona autorizada que utiliza el sistema mediante una cuenta registrada.
Administrador: Usuario con privilegios especiales para gestionar cuentas, permisos y configuraciones del sistema.
Datos: Informacion registrada dentro del sistema, incluyendo usuarios, tareas, documentos y registros de auditoria.

3. Uso permitido del sistema
El sistema SecureDesk debera utilizarse exclusivamente para fines organizacionales legitimos, incluyendo la gestion de tareas internas, el registro de actividades laborales, la administracion de documentos organizacionales y el monitoreo de actividades del sistema.
Queda estrictamente prohibido utilizar el sistema para actividades ilicitas, acceso no autorizado a informacion, manipulacion o alteracion indebida de datos e intentos de vulnerar la seguridad del sistema.

4. Registro y acceso de usuarios
El acceso al sistema se realiza mediante credenciales personales asignadas por un administrador autorizado.
Cada usuario es responsable de mantener la confidencialidad de su contrasena, no compartir sus credenciales con terceros y notificar al administrador en caso de sospecha de uso indebido de su cuenta.
El sistema podra bloquear temporalmente cuentas que registren multiples intentos fallidos de inicio de sesion como medida de seguridad.

5. Seguridad de la informacion
SecureDesk implementa mecanismos de seguridad para proteger la informacion almacenada en el sistema, incluyendo control de accesos basado en roles, registro de auditoria, bloqueo de cuentas tras intentos fallidos, validacion y sanitizacion de datos y uso de almacenamiento seguro mediante servicios en la nube.
Sin embargo, el usuario reconoce que ningun sistema es completamente invulnerable, por lo que debe utilizar la aplicacion de manera responsable.

6. Gestion de documentos
Los documentos cargados al sistema deberan cumplir con las politicas internas de la organizacion.
El usuario es responsable de verificar la veracidad de los documentos cargados, no subir informacion ilegal o no autorizada y respetar derechos de autor y propiedad intelectual.
El sistema podra aplicar mecanismos de integridad documental mediante el uso de firmas digitales o hash criptograficos.

7. Registro de actividades
Con el objetivo de mantener la seguridad y trazabilidad del sistema, SecureDesk registra eventos relevantes tales como inicio y cierre de sesion, creacion o modificacion de tareas, registro de documentos y cambios en cuentas de usuario.
Estos registros forman parte del sistema de auditoria del sistema.

8. Responsabilidades del usuario
El usuario se compromete a utilizar el sistema unicamente para fines autorizados, proteger sus credenciales de acceso, no intentar vulnerar la seguridad del sistema y respetar la integridad de los datos almacenados.
El incumplimiento de estas responsabilidades podra derivar en la suspension o eliminacion de la cuenta del usuario.

9. Disponibilidad del servicio
El sistema podra experimentar interrupciones temporales debido a mantenimiento tecnico, actualizaciones del sistema o problemas de infraestructura.
La organizacion no garantiza disponibilidad continua del servicio.

10. Proteccion de datos
La informacion registrada en el sistema sera tratada conforme a las politicas internas de la organizacion y a la normativa aplicable en materia de proteccion de datos personales.
Los datos recopilados seran utilizados unicamente para fines operativos relacionados con el funcionamiento del sistema.

11. Modificaciones de los terminos
La organizacion se reserva el derecho de modificar los presentes Terminos y Condiciones en cualquier momento.
Los cambios seran comunicados a los usuarios a traves del sistema.

12. Aceptacion de los terminos
Al utilizar el sistema SecureDesk, el usuario declara haber leido, entendido y aceptado los presentes Terminos y Condiciones de uso.""",
                self.terms_var,
                "Acepto los terminos y condiciones de uso",
            ),
            (
                "Aviso de Privacidad",
                "Explica que datos recopila SecureDesk, para que se usan, como se protegen y los derechos del usuario sobre su informacion.",
                """Sistema: SecureDesk
Version: 1.0
Ultima actualizacion: 2026

1. Responsable del tratamiento de los datos
La aplicacion SecureDesk es responsable del tratamiento y proteccion de los datos personales que los usuarios proporcionan al utilizar el sistema.
El sistema ha sido desarrollado para gestionar tareas, documentos y actividades dentro de una organizacion, garantizando la seguridad y confidencialidad de la informacion almacenada.

2. Datos personales recopilados
Para el funcionamiento del sistema SecureDesk se podran recopilar los siguientes datos personales: nombre del usuario, direccion de correo electronico, nombre de usuario, informacion de acceso al sistema, registros de actividad dentro del sistema y documentos o archivos cargados por el usuario.
Estos datos son necesarios para la correcta operacion del sistema.

3. Finalidad del tratamiento de los datos
Los datos personales recopilados seran utilizados exclusivamente para identificar a los usuarios dentro del sistema, permitir el acceso seguro a la aplicacion, gestionar tareas y actividades organizacionales, registrar eventos del sistema para fines de auditoria y seguridad y administrar documentos relacionados con las actividades del sistema.
Los datos no seran utilizados para fines comerciales ni publicitarios.

4. Proteccion de la informacion
SecureDesk implementa diversas medidas de seguridad para proteger la informacion almacenada en el sistema, incluyendo control de acceso basado en roles, registro de auditoria de eventos, validacion de datos ingresados, proteccion de credenciales y uso de almacenamiento seguro mediante servicios en la nube.
Estas medidas tienen como objetivo prevenir accesos no autorizados, alteracion o perdida de informacion.

5. Conservacion de los datos
Los datos personales seran conservados unicamente durante el tiempo necesario para cumplir con las finalidades descritas en este aviso.
Una vez que los datos ya no sean necesarios, podran ser eliminados o anonimizados conforme a las politicas de la organizacion.

6. Derechos del usuario
Los usuarios del sistema tienen derecho a acceder a la informacion registrada sobre ellos, solicitar la correccion de datos incorrectos, solicitar la eliminacion de sus datos cuando sea aplicable y conocer el uso que se da a su informacion personal.
Las solicitudes relacionadas con estos derechos deberan dirigirse al administrador del sistema.

7. Uso de registros de actividad
El sistema registra informacion relacionada con la actividad de los usuarios, incluyendo inicio y cierre de sesion, acciones realizadas dentro del sistema y registro de tareas o documentos.
Estos registros se utilizan exclusivamente con fines de seguridad, monitoreo y auditoria del sistema.

8. Transferencia de datos
La informacion almacenada en el sistema podra ser gestionada mediante servicios de almacenamiento en la nube para garantizar su disponibilidad y seguridad.
No se compartiran datos personales con terceros sin autorizacion, salvo cuando sea requerido por la ley o por politicas internas de la organizacion.

9. Cambios en el aviso de privacidad
La organizacion se reserva el derecho de modificar el presente Aviso de Privacidad en cualquier momento.
Las actualizaciones seran notificadas a los usuarios a traves del sistema.

10. Aceptacion del aviso de privacidad
El uso del sistema SecureDesk implica que el usuario ha leido y acepta el presente Aviso de Privacidad.""",
                self.privacy_var,
                "Acepto el aviso de privacidad",
            ),
            (
                "Acuerdo de Confidencialidad",
                "Establece como debe manejarse la informacion sensible del sistema y las obligaciones del usuario para protegerla.",
                """Sistema: SecureDesk
Version: 1.0
Ultima actualizacion: 2026

1. Introduccion
El presente Acuerdo de Confidencialidad establece las condiciones bajo las cuales los usuarios autorizados del sistema SecureDesk deberan manejar la informacion a la que tengan acceso durante el uso de la aplicacion.
El objetivo de este acuerdo es proteger la informacion sensible de la organizacion y garantizar el uso responsable de los datos almacenados dentro del sistema.

2. Definicion de informacion confidencial
Se considera informacion confidencial toda aquella informacion a la que el usuario tenga acceso dentro del sistema SecureDesk, incluyendo informacion de usuarios del sistema, datos de tareas y actividades organizacionales, documentos cargados dentro del sistema, registros de auditoria del sistema e informacion interna de la organizacion.
La informacion confidencial podra encontrarse en formato digital dentro del sistema.

3. Obligaciones del usuario
El usuario se compromete a utilizar la informacion unicamente para fines autorizados por la organizacion, no divulgar informacion confidencial a personas no autorizadas, no copiar, distribuir o modificar informacion sin autorizacion, proteger sus credenciales de acceso al sistema y notificar inmediatamente cualquier incidente de seguridad detectado.

4. Restricciones de uso
El usuario no podra compartir informacion confidencial con terceros, utilizar la informacion para fines personales o ajenos a la organizacion, intentar acceder a informacion para la cual no tiene permisos ni manipular o alterar informacion sin autorizacion.
Cualquier incumplimiento podra derivar en la suspension del acceso al sistema y posibles acciones disciplinarias.

5. Proteccion de la informacion
El sistema SecureDesk implementa controles de seguridad para proteger la informacion, incluyendo control de acceso basado en roles, registro de auditoria de actividades, validacion de datos, proteccion de credenciales de acceso y monitoreo de actividades dentro del sistema.

6. Duracion del acuerdo
Las obligaciones de confidencialidad establecidas en este acuerdo permaneceran vigentes durante todo el tiempo que el usuario tenga acceso al sistema y continuaran aplicandose incluso despues de que dicho acceso haya finalizado.

7. Incidentes de seguridad
En caso de que el usuario detecte accesos no autorizados, perdida de informacion o uso indebido del sistema, debera reportarlo inmediatamente al administrador del sistema.

8. Aceptacion del acuerdo
El uso del sistema SecureDesk implica que el usuario ha leido, entendido y acepta cumplir con el presente Acuerdo de Confidencialidad.""",
                self.confidentiality_var,
                "Acepto el acuerdo de confidencialidad",
            ),
        ]:
            self._build_expandable_notice(panel, title, summary, text, variable, label)

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
            self.terms_var.get(),
            self.confidentiality_var.get(),
        )

    def set_message(self, message: str) -> None:
        self.message_var.set(message)

    def _build_expandable_notice(self, parent, title: str, summary: str, text: str, variable, label: str) -> None:
        card = tk.Frame(parent, bg="#F7FAFD", highlightbackground="#D5DFEA", highlightthickness=1)
        card.pack(fill="x", pady=(0, 14))

        header = ttk.Frame(card, style="Card.TFrame")
        header.pack(fill="x", padx=16, pady=(14, 8))
        ttk.Label(header, text=title, style="PanelTitle.TLabel").pack(side="left", anchor="w")

        body = ttk.Frame(card, style="Card.TFrame")
        summary_label = ttk.Label(
            card,
            text=summary,
            style="PanelText.TLabel",
            wraplength=700,
            justify="left",
        )
        summary_label.pack(anchor="w", padx=16, pady=(0, 10))

        toggle_button = ttk.Button(header, text="Expandir", style="Secondary.TButton", width=12)
        toggle_button.pack(side="right")

        text_shell = tk.Frame(body, bg="#F7FAFD", highlightbackground="#D5DFEA", highlightthickness=1)
        text_shell.pack(fill="x", padx=14, pady=(0, 10))
        text_widget = tk.Text(
            text_shell,
            height=14,
            wrap="word",
            font=("Segoe UI", 10),
            bd=0,
            bg="#F7FAFD",
            fg="#5D7288",
            yscrollcommand=lambda first, last: scroll.set(first, last),
        )
        text_widget.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=10)
        scroll = ttk.Scrollbar(text_shell, orient="vertical", command=text_widget.yview)
        scroll.pack(side="right", fill="y", padx=(8, 10), pady=10)
        text_widget.insert("1.0", text)
        text_widget.configure(state="disabled")

        agree_shell = tk.Frame(body, bg="#EEF3F8", highlightbackground="#D5DFEA", highlightthickness=1)
        agree_shell.pack(fill="x", padx=14, pady=(0, 14))
        ttk.Checkbutton(agree_shell, text=label, variable=variable).pack(anchor="w", padx=12, pady=12)

        expanded = {"value": False}

        def toggle() -> None:
            expanded["value"] = not expanded["value"]
            if expanded["value"]:
                body.pack(fill="x")
                toggle_button.configure(text="Ocultar")
            else:
                body.pack_forget()
                toggle_button.configure(text="Expandir")

        toggle_button.configure(command=toggle)

    def _toggle_password_visibility(self) -> None:
        visible = not self.show_password_var.get()
        self.show_password_var.set(visible)
        self.password_entry.configure(show="" if visible else "*")
        self.password_toggle.configure(text="Ocultar" if visible else "Ver")

    def _validate_password(self) -> None:
        valid, message = validate_password_policy(self.password_var.get())
        self.password_feedback.configure(
            text=message,
            style="SuccessFeedback.TLabel" if valid else "ErrorFeedback.TLabel",
        )
