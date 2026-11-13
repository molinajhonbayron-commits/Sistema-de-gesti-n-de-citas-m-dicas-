# Sistema de Gestión de Citas Médicas

Aplicación web desarrollada con Django para administrar una clínica: registro de pacientes,
agenda de médicos, solicitud y gestión de citas, historial clínico, reportes e ingresos, y
recordatorios de citas por correo electrónico.

## Funcionalidades
- Inicio de sesión por roles: **administrador, recepcionista, médico y paciente** (cada uno ve un menú distinto).
- Registro de pacientes nuevos en `/registro/`.
- **Pacientes**, **médicos** y **usuarios**: alta, listado y edición.
- **Citas**: solicitar, agendar, confirmar, cancelar y consultar la agenda del médico.
- **Historial clínico** por paciente y por consulta.
- **Reportes**: resumen (dashboard), reporte de citas e ingresos.
- **Recordatorios por correo** de las citas de mañana (`enviar_recordatorios`).
- Configuración de especialidades y consultorios desde el panel `/admin/`.

## Tecnologías usadas
- Python 3.10+
- Django 4.2+
- SQLite (base de datos por defecto)
- HTML + plantillas de Django
- Bootstrap 5.3 y Bootstrap Icons (por CDN)
- python-dotenv (variables de entorno)

## Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/TU_USUARIO/NOMBRE_REPO.git
   cd NOMBRE_REPO
   ```
2. **Crear y activar un entorno virtual**
   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   source venv/bin/activate       # Linux / macOS
   ```
3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configurar variables de entorno** (opcional: sin `.env` funciona con valores de desarrollo)
   ```bash
   copy .env.example .env         # Windows
   cp .env.example .env           # Linux / macOS
   ```
5. **Crear la base de datos y cargar datos de ejemplo**
   ```bash
   python manage.py migrate
   python manage.py cargar_demo
   ```
6. **Ejecutar el servidor**
   ```bash
   python manage.py runserver
   ```
   Abrir http://127.0.0.1:8000

## Usuarios de demostración
| Rol | Usuario | Clave |
|---|---|---|
| Administrador | `admin` | `admin12345` |
| Recepción | `recepcion` | `recep12345` |
| Médico | `medico1`, `medico2`, `medico3` | `medico12345` |
| Paciente | `paciente1` | `paciente12345` |

> Solo para pruebas. Cámbialas si despliegas en un servidor real.

## Configuración (.env)
| Variable | Descripción | Por defecto |
|---|---|---|
| `SECRET_KEY` | Clave secreta de Django | clave de desarrollo |
| `DEBUG` | `True` en desarrollo, `False` en producción | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por coma | `127.0.0.1,localhost` |
| `EMAIL_BACKEND` | Backend de correo | consola |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Solo para enviar correo real por SMTP | vacío |

**Conexión a base de datos:** el proyecto usa SQLite (`db.sqlite3`), que se crea automáticamente
con `python manage.py migrate`. No necesita servidor ni credenciales.

## Recordatorios por correo
```bash
python manage.py enviar_recordatorios
```
Envía el recordatorio de las citas de mañana (pendientes o confirmadas). Por defecto los correos
se muestran en la consola; para enviarlos de verdad configura SMTP en `.env`. Se puede programar
con cron (Linux) o el Programador de tareas (Windows).

## Estructura del proyecto
```
config/      configuración de Django, utilidades y menú por rol
usuarios/    autenticación, roles, registro y comando cargar_demo
pacientes/   gestión de pacientes
medicos/     médicos, especialidades y horarios
citas/       solicitud, agenda y estados de las citas
historial/   historial clínico y comando enviar_recordatorios
reportes/    dashboard, reporte de citas e ingresos
templates/   plantillas HTML
static/      archivos estáticos (CSS)
```

## Autor
bayron – molinajhonbayron@gmail.com
