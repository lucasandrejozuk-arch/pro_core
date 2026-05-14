# PRO CORE

PRO CORE is a desktop management platform for small and medium technical assistance companies, focused on service orders.

## Stack

- Backend: Python + FastAPI
- Frontend: Qt for Python / PySide6
- Database: PostgreSQL
- Infrastructure: Docker Compose for local development
- IDE: Visual Studio Code
- Versioning: Git and GitHub

## MVP Scope

- Splash screen with functional progress bar
- Login screen
- Required password change on first access
- Dashboard
- Service orders
- Equipment
- Inventory
- Customers
- Settings
- Administrative area
- Basic reports and exports

## Local Development

Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Start PostgreSQL:

```powershell
docker compose up -d postgres
```

Apply database migrations:

```powershell
alembic upgrade head
```

Create the first administrator:

```powershell
python scripts/create_initial_admin.py --company-name "Minha Assistencia" --admin-name "Administrador" --email admin@example.com --password "ChangeMe123"
```

Run the backend:

```powershell
uvicorn backend.app.main:app --reload
```

Run the frontend:

```powershell
python frontend/app/main.py
```

## Database Backups

Create a backup from the application in `Configuracoes` with `Executar backup agora`.
Backup files are written to the configured backup folder, which defaults to `backups/`.

Restore a backup into the local Docker PostgreSQL container:

```powershell
python scripts/restore_database_backup.py --dump-file .\backups\pro_core_YYYYMMDD_HHMMSS.dump
```

Restoring uses `pg_restore --clean --if-exists`, so it replaces objects in the target database.

## Project Principles

- DRY: avoid duplicated business logic.
- KISS: prefer simple, readable solutions.
- YAGNI: build what the MVP needs now.
