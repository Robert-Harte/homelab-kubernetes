#!/usr/bin/env python3
"""
PostgreSQL Database Backup Script
Backs up every database on a PostgreSQL server using pg_dump.
Filenames include the database name and the date of the backup.
"""

import subprocess
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration – edit these or override via environment variables
# ---------------------------------------------------------------------------
PG_HOST     = os.getenv("PG_HOST",     "localhost")
PG_PORT     = os.getenv("PG_PORT",     "5432")
PG_USER     = os.getenv("PG_USER",     "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")          # leave blank to use .pgpass
BACKUP_DIR  = os.getenv("BACKUP_DIR",  "./pg_backups")
BACKUP_FORMAT = os.getenv("BACKUP_FORMAT", "custom")  # custom | plain | directory | tar

# Databases to skip (system databases that don't need user backups)
SKIP_DATABASES = {"template0", "template1"}
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def build_env() -> dict:
    """Return an environment dict that includes PGPASSWORD if set."""
    env = os.environ.copy()
    if PG_PASSWORD:
        env["PGPASSWORD"] = PG_PASSWORD
    return env


def list_databases(env: dict) -> list[str]:
    """Return all user-facing database names from the PostgreSQL server."""
    cmd = [
        "psql",
        "--host", PG_HOST,
        "--port", PG_PORT,
        "--username", PG_USER,
        "--no-password",
        "--tuples-only",
        "--command", "SELECT datname FROM pg_database WHERE datistemplate = false;",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=True)
    databases = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return [db for db in databases if db not in SKIP_DATABASES]


def backup_database(db_name: str, backup_dir: Path, timestamp: str, env: dict) -> Path:
    """
    Back up a single database with pg_dump.
    Returns the path of the created backup file.
    """
    extension_map = {
        "custom":    ".dump",
        "plain":     ".sql",
        "directory": "",        # pg_dump creates a directory, not a file
        "tar":       ".tar",
    }
    ext = extension_map.get(BACKUP_FORMAT, ".dump")
    filename = f"{db_name}_{timestamp}{ext}"
    output_path = backup_dir / filename

    cmd = [
        "pg_dump",
        "--host",     PG_HOST,
        "--port",     PG_PORT,
        "--username", PG_USER,
        "--no-password",
        "--format",   BACKUP_FORMAT,
        "--file",     str(output_path),
        db_name,
    ]

    log.info("  Backing up '%s' → %s", db_name, output_path)
    subprocess.run(cmd, env=env, check=True)
    return output_path


def main() -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_dir = Path(BACKUP_DIR)
    backup_dir.mkdir(parents=True, exist_ok=True)

    log.info("PostgreSQL backup started")
    log.info("  Host      : %s:%s", PG_HOST, PG_PORT)
    log.info("  User      : %s",    PG_USER)
    log.info("  Format    : %s",    BACKUP_FORMAT)
    log.info("  Output dir: %s",    backup_dir.resolve())

    env = build_env()

    try:
        databases = list_databases(env)
    except subprocess.CalledProcessError as exc:
        log.error("Failed to list databases: %s", exc.stderr)
        sys.exit(1)

    if not databases:
        log.warning("No databases found – nothing to back up.")
        return

    log.info("Found %d database(s): %s", len(databases), ", ".join(databases))

    successes, failures = [], []

    for db in databases:
        try:
            path = backup_database(db, backup_dir, timestamp, env)
            successes.append((db, path))
        except subprocess.CalledProcessError as exc:
            log.error("  FAILED '%s': %s", db, exc.stderr or exc)
            failures.append(db)

    log.info("─" * 60)
    log.info("Backup complete: %d succeeded, %d failed", len(successes), len(failures))
    for db, path in successes:
        size = os.path.getsize(path) if path.exists() else 0
        log.info("  ✓  %-30s  %s  (%.1f KB)", db, path.name, size / 1024)
    for db in failures:
        log.error("  ✗  %s", db)

    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()