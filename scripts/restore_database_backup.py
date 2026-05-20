from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Restore a PRO CORE PostgreSQL backup dump.")
    parser.add_argument("--dump-file", required=True, help="Path to the .dump file.")
    parser.add_argument(
        "--container", default="pro_core_postgres", help="PostgreSQL Docker container."
    )
    parser.add_argument("--database", default="pro_core", help="Target database name.")
    parser.add_argument("--user", default="pro_core", help="PostgreSQL user.")
    return parser.parse_args()


def run_command(command: list[str], error_message: str) -> None:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise SystemExit(f"{error_message} {detail}".strip())


def main() -> int:
    args = parse_args()
    dump_file = Path(args.dump_file).expanduser().resolve()
    if not dump_file.exists():
        raise SystemExit(f"Backup file not found: {dump_file}")

    container_path = f"/tmp/{dump_file.name}"
    run_command(
        ["docker", "cp", str(dump_file), f"{args.container}:{container_path}"],
        "Could not copy backup file to Docker.",
    )
    run_command(
        [
            "docker",
            "exec",
            args.container,
            "pg_restore",
            "-U",
            args.user,
            "-d",
            args.database,
            "--clean",
            "--if-exists",
            container_path,
        ],
        "Could not restore backup.",
    )

    print(f"Backup restored into database '{args.database}' from {dump_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
