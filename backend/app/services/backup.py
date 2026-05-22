from __future__ import annotations

import os
import shutil
import subprocess
import uuid
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from backend.app.core.config import Settings, get_settings
from backend.app.models.configuration import BackupPolicy
from backend.app.services.configuration import _get_company, get_or_create_backup_policy

POSTGRES_CONTAINER_NAME = "pro_core_postgres"


def run_database_backup(
    db: Session,
    company_id: uuid.UUID,
    settings: Settings | None = None,
) -> dict:
    runtime_settings = settings or get_settings()
    company = _get_company(db, company_id)
    backup_policy = get_or_create_backup_policy(db, company)
    backup_dir = _resolve_backup_dir(backup_policy)
    backup_dir.mkdir(parents=True, exist_ok=True)

    created_at = datetime.now(UTC)
    file_name = f"pro_core_{created_at:%Y%m%d_%H%M%S}.dump"
    target_path = backup_dir / file_name

    if _is_docker_container_available(POSTGRES_CONTAINER_NAME):
        _run_docker_backup(runtime_settings, file_name, target_path)
        _validate_docker_backup(file_name, runtime_settings)
    else:
        _run_local_backup(runtime_settings, target_path)
        _validate_local_backup(target_path, runtime_settings)

    backup_policy.last_run_at = created_at
    db.add(backup_policy)
    db.commit()

    return {
        "file_name": file_name,
        "file_path": str(target_path),
        "file_size_bytes": target_path.stat().st_size,
        "created_at": created_at,
        "validated": True,
    }


def _resolve_backup_dir(backup_policy: BackupPolicy) -> Path:
    storage_path = Path(backup_policy.storage_path).expanduser()
    if storage_path.is_absolute():
        return storage_path
    return Path.cwd() / storage_path


def _is_docker_container_available(container_name: str) -> bool:
    if shutil.which("docker") is None:
        return False

    try:
        result = subprocess.run(
            [
                "docker",
                "inspect",
                "-f",
                "{{.State.Running}}",
                container_name,
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        return False
    return result.returncode == 0 and result.stdout.strip().lower() == "true"


def _run_docker_backup(settings: Settings, file_name: str, target_path: Path) -> None:
    container_path = f"/tmp/{file_name}"
    _run_command(
        [
            "docker",
            "exec",
            POSTGRES_CONTAINER_NAME,
            "pg_dump",
            "-U",
            settings.postgres_user,
            "-d",
            settings.postgres_db,
            "-F",
            "c",
            "-f",
            container_path,
        ],
        "Database backup failed inside Docker.",
        timeout_seconds=settings.pro_core_backup_command_timeout_seconds,
    )
    _run_command(
        [
            "docker",
            "cp",
            f"{POSTGRES_CONTAINER_NAME}:{container_path}",
            str(target_path),
        ],
        "Could not copy backup file from Docker.",
        timeout_seconds=settings.pro_core_backup_command_timeout_seconds,
    )


def _validate_docker_backup(file_name: str, settings: Settings) -> None:
    _run_command(
        [
            "docker",
            "exec",
            POSTGRES_CONTAINER_NAME,
            "pg_restore",
            "--list",
            f"/tmp/{file_name}",
        ],
        "Backup validation failed inside Docker.",
        timeout_seconds=settings.pro_core_backup_command_timeout_seconds,
    )


def _run_local_backup(settings: Settings, target_path: Path) -> None:
    if shutil.which("pg_dump") is None:
        raise RuntimeError("pg_dump not found. Install PostgreSQL client tools or use Docker.")

    _run_command(
        [
            "pg_dump",
            "-h",
            settings.postgres_host,
            "-p",
            str(settings.postgres_port),
            "-U",
            settings.postgres_user,
            "-d",
            settings.postgres_db,
            "-F",
            "c",
            "-f",
            str(target_path),
        ],
        "Database backup failed.",
        env={"PGPASSWORD": settings.postgres_password},
        timeout_seconds=settings.pro_core_backup_command_timeout_seconds,
    )


def _validate_local_backup(target_path: Path, settings: Settings | None = None) -> None:
    if shutil.which("pg_restore") is None:
        raise RuntimeError("pg_restore not found. Install PostgreSQL client tools or use Docker.")

    runtime_settings = settings or get_settings()
    _run_command(
        ["pg_restore", "--list", str(target_path)],
        "Backup validation failed.",
        timeout_seconds=runtime_settings.pro_core_backup_command_timeout_seconds,
    )


def _run_command(
    command: list[str],
    error_message: str,
    env: dict[str, str] | None = None,
    timeout_seconds: int | None = None,
) -> None:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            env=({**os.environ, **env} if env else None),
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"{error_message} Command timed out.") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"{error_message} {detail}".strip())
