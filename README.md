# SecureDesk

Aplicacion de escritorio segura construida con Python, Tkinter y Firebase Cloud Firestore para la gestion interna de usuarios, tareas, documentos y auditoria.

## Funcionalidades incluidas

- Inicio de sesion seguro con hash PBKDF2, control de intentos fallidos y bloqueo temporal.
- Dashboard corporativo con menu lateral y paneles por modulo.
- Gestion de usuarios con roles, estados y control de acceso administrativo.
- Alta de usuarios solo por administrador con contrasena provisional.
- Primer acceso obligatorio con cambio de contrasena y aceptacion de avisos.
- Gestion de tareas con prioridad, estado, responsable y fecha limite.
- Registro documental con hash SHA-256 para integridad.
- Auditoria centralizada de eventos criticos.
- Sesiones con vencimiento por inactividad.

## Ejecucion

1. Coloca tu archivo de credenciales Firebase en `llaveKey.json`.
2. Instala dependencias:

```powershell
pip install -r requirements.txt
```

3. Ejecuta la aplicacion:

```powershell
python main.py
```

## Acceso inicial

Si la coleccion `usuarios` esta vacia, el sistema crea automaticamente un usuario administrador inicial:

- Usuario: `admin`
- Contrasena: `Admin123!`

Se recomienda cambiar esta contrasena en cuanto se prepare la siguiente iteracion del sistema.

Tambien puedes sobrescribir estos valores con variables de entorno:

- `SECUREDESK_BOOTSTRAP_USER`
- `SECUREDESK_BOOTSTRAP_PASSWORD`

## Colecciones Firestore esperadas

- `usuarios`
- `tareas`
- `documentos`
- `auditoria`
