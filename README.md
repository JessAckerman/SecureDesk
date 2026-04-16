# SecureDesk

Aplicacion de escritorio segura construida con Python, Tkinter y Firebase Cloud Firestore para la gestion interna de usuarios, tareas, documentos y auditoria.

## Funcionalidades incluidas

- Inicio de sesion seguro con hash PBKDF2, control de intentos fallidos y bloqueo temporal.
- Dashboard corporativo con menu lateral y paneles por modulo.
- Gestion de usuarios con roles, estados y control de acceso administrativo.
- Alta de usuarios solo por administrador con contrasena provisional enviada por correo.
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

## Configuracion de correo

Para que la contrasena provisional llegue automaticamente al correo del nuevo usuario, configura estas variables de entorno antes de ejecutar la aplicacion:

- `SECUREDESK_SMTP_HOST`
- `SECUREDESK_SMTP_PORT`
- `SECUREDESK_SMTP_USERNAME`
- `SECUREDESK_SMTP_PASSWORD`
- `SECUREDESK_SMTP_USE_TLS`
- `SECUREDESK_SMTP_FROM_EMAIL`
- `SECUREDESK_SMTP_FROM_NAME`

Ejemplo en PowerShell:

```powershell
$env:SECUREDESK_SMTP_HOST="smtp.office365.com"
$env:SECUREDESK_SMTP_PORT="587"
$env:SECUREDESK_SMTP_USERNAME="notificaciones@tuempresa.com"
$env:SECUREDESK_SMTP_PASSWORD="tu-clave-o-app-password"
$env:SECUREDESK_SMTP_USE_TLS="true"
$env:SECUREDESK_SMTP_FROM_EMAIL="notificaciones@tuempresa.com"
$env:SECUREDESK_SMTP_FROM_NAME="SecureDesk"
```

Si el correo no esta configurado o falla el envio, el usuario no se registra para evitar cuentas activas sin entrega de credenciales.

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

$env:SECUREDESK_SMTP_HOST="smtp.gmail.com"
$env:SECUREDESK_SMTP_PORT="587"
$env:SECUREDESK_SMTP_USERNAME="2321082996@alumno.utpuebla.edu.mx"
$env:SECUREDESK_SMTP_PASSWORD="afbk nryk tedw qvgx"
$env:SECUREDESK_SMTP_USE_TLS="true"
$env:SECUREDESK_SMTP_FROM_EMAIL="2321082996@alumno.utpuebla.edu.mx"
$env:SECUREDESK_SMTP_FROM_NAME="SecureDesk"
python launch_dual_demo.py

python main.py
