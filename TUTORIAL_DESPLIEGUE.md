y# 🚀 Tutorial de Despliegue en Render — CorpSystem (Python/Flask)

## Resumen de la migración

| Concepto | Node.js (original) | Python (nuevo) |
|---|---|---|
| Framework | Express.js | Flask 3.0 |
| Plantillas | EJS | Jinja2 |
| Base de datos | mssql (SQL Server) | pymssql |
| Auth | jsonwebtoken | PyJWT |
| Subida de archivos | multer | Werkzeug |
| Cloudinary | cloudinary npm | cloudinary pip |
| Servidor producción | node app.js | gunicorn |
| Config | package.json | requirements.txt + Procfile |

---

## Paso 1 — Preparar el repositorio

```bash
cd proyecto-python
git init
git add .
git commit -m "first commit: migrate to Flask"
```

Sube el código a GitHub (o GitLab):

```bash
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git branch -M main
git push -u origin main
```

---

## Paso 2 — Crear el servicio en Render

1. Ve a **https://render.com** e inicia sesión.
2. Click en **"New +"** → **"Web Service"**.
3. Conecta tu repositorio de GitHub.
4. Configura:

| Campo | Valor |
|---|---|
| **Name** | corpsystem (o el nombre que prefieras) |
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| **Instance Type** | Free (o el que necesites) |

---

## Paso 3 — Variables de entorno

En Render, ve a **Environment** y agrega estas variables:

```
DB_SERVER        = db38571.public.databaseasp.net
DB_USER          = db38571
DB_PASSWORD      = wP_4T2s?z+9G
DB_NAME          = db38571
DB_PORT          = 1433
SECRET_KEY       = (genera una clave larga y aleatoria)
JWT_SECRET       = (genera una clave larga y aleatoria)
RECAPTCHA_SITE   = 6LebTlYsAAAAADnLSamRI9p-VJYYovtlyxHeRD-8
RECAPTCHA_SECRET = 6LebTlYsAAAAAD0Q3XM3e6ah7CctvUEK4OEclWDR
CLOUDINARY_CLOUD_NAME = dqhqrjoe6
CLOUDINARY_API_KEY    = 359285996587242
CLOUDINARY_API_SECRET = (tu secret de Cloudinary)
```

> **Tip:** Para `SECRET_KEY` y `JWT_SECRET` usa un generador:
> ```python
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

---

## Paso 4 — Desplegar

1. Click en **"Create Web Service"**.
2. Render ejecutará automáticamente `pip install -r requirements.txt`.
3. Luego lanzará gunicorn.
4. El log mostrará: `Booting worker with pid: ...`

Tu app estará en: `https://TU-NOMBRE.onrender.com`

---

## Paso 5 — Prueba local antes de subir

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
cp .env.example .env
# Edita .env con tus valores reales

# Ejecutar
python app.py
```

Abre http://localhost:3000

---

## Notas importantes

### Diferencias clave vs Node.js

1. **Plantillas EJS → Jinja2**
   - `<%= variable %>` → `{{ variable }}`
   - `<%- JSON.stringify(data) %>` → `{{ data | tojson }}`
   - `<% if (x) { %>` → `{% if x %}`

2. **Rutas Express → Flask Blueprints**
   - `router.get('/ruta', ...)` → `@bp.route('/ruta')`
   - Middleware como decoradores (`@require_auth`)

3. **SQL Server connection pool**
   - En Python se usa `pymssql` con conexiones por request (no un pool global como en Node)
   - Cada llamada a `execute_query()` abre y cierra la conexión automáticamente

4. **Archivos estáticos en Render**
   - La carpeta `uploads/` en el plan Free de Render es **efímera** (se borra al redesplegar)
   - Para producción se recomienda subir imágenes a Cloudinary (ya implementado en `/upload-image`)

5. **gunicorn workers**
   - Con 2 workers el plan Free de Render funciona sin problemas
   - Para más tráfico aumenta workers: `--workers 4`

---

## Estructura del proyecto

```
proyecto-python/
├── app.py                    # Punto de entrada Flask
├── requirements.txt          # Dependencias Python
├── Procfile                  # Comando de inicio para Render
├── render.yaml               # Config de despliegue Render
├── .env.example              # Plantilla de variables de entorno
├── config/
│   └── db.py                 # Conexión SQL Server (pymssql)
├── middleware/
│   └── auth.py               # JWT, require_auth, load_permissions
├── routes/
│   ├── auth_routes.py        # Login, dashboard, logout
│   ├── crud_routes.py        # APIs: perfiles, módulos, permisos, usuarios
│   ├── ftp_routes.py         # Cloudinary upload/list
│   ├── seguridad_routes.py   # Vistas del módulo seguridad
│   └── static_routes.py      # Módulos estáticos (principal-1-1, etc.)
├── services/
│   └── dashboard_data.py     # Consulta de menús y datos del usuario
├── templates/
│   ├── login.html            # Pantalla de login (diseño renovado)
│   ├── dashboard.html        # Dashboard principal con todo el JS
│   └── error.html            # Página de error 404/500
└── uploads/
    └── users/                # Fotos de usuarios (subidas localmente)
```
