#!/usr/bin/env python3
"""
PostgreSQL Database Backup Script
Backs up every database on a PostgreSQL server by executing pg_dump
inside a Kubernetes pod via kubectl exec.
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
K8S_NAMESPACE = os.getenv("K8S_NAMESPACE", "database")
K8S_POD       = os.getenv("K8S_POD",       "postgres-0")
PG_USER       = os.getenv("PG_USER",       "robert")
PG_PASSWORD   = os.getenv("PG_PASSWORD",   "")   # leave blank to rely on trust/peer auth
BACKUP_DIR    = os.getenv("BACKUP_DIR",    "/media/storage/Backups/Databases/")
BACKUP_FORMAT = os.getenv("BACKUP_FORMAT", "custom")  # custom | plain | directory | tar
POD_TEMP_DIR  = os.getenv("POD_TEMP_DIR",  "/var/lib/postgresql")
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

SKIP_DATABASES = {"template0", "template1", "robert", "tmp"}


def pg_cmd(*args) -> list[str]:
    """Wrap a pg command with PGPASSWORD if a password is configured."""
    if PG_PASSWORD:
        return ["env", f"PGPASSWORD={PG_PASSWORD}", *args]
    return list(args)


def kubectl_exec(*args, **kwargs) -> subprocess.CompletedProcess:
    """Run a command inside the configured Kubernetes pod."""
    cmd = ["kubectl", "exec", "-n", K8S_NAMESPACE, K8S_POD, "--", *args]
    return subprocess.run(cmd, **kwargs)


def list_databases() -> list[str]:
    """Return all user-facing database names from the pod's PostgreSQL server."""
    result = kubectl_exec(
        *pg_cmd(
            "psql",
            "--username", PG_USER,
            "--no-password",
            "--tuples-only",
            "--command", "SELECT datname FROM pg_database WHERE datistemplate = false;",
        ),
        capture_output=True,
        text=True,
        check=True,
    )
    databases = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return [db for db in databases if db not in SKIP_DATABASES]


def backup_database(db_name: str, backup_dir: Path, timestamp: str) -> Path:
    """
    Back up a single database via pg_dump inside the Kubernetes pod.
    For non-directory formats: streams pg_dump stdout directly to a local file.
    For directory format: writes inside the pod then copies out via kubectl cp.
    Returns the path of the created backup file.
    """
    extension_map = {
        "custom":    ".dump",
        "plain":     ".sql",
        "directory": "",
        "tar":       ".tar",
    }
    ext = extension_map.get(BACKUP_FORMAT, ".dump")
    filename = f"{db_name}_{timestamp}{ext}"
    output_path = backup_dir / filename

    log.info("  Backing up '%s' → %s", db_name, output_path)

    if BACKUP_FORMAT == "directory":
        # directory format cannot stream to stdout; write inside the pod then copy out.
        pod_path = f"{POD_TEMP_DIR}/{filename}"
        kubectl_exec(
            *pg_cmd(
                "pg_dump",
                "--username", PG_USER,
                "--no-password",
                "--format", BACKUP_FORMAT,
                "--file", pod_path,
                db_name,
            ),
            check=True,
        )
        subprocess.run(
            ["kubectl", "cp", "-n", K8S_NAMESPACE, f"{K8S_POD}:{pod_path}", str(output_path)],
            check=True,
        )
        kubectl_exec("rm", "-rf", pod_path, check=False)
    else:
        # Stream pg_dump stdout directly into a local file.
        cmd = [
            "kubectl", "exec", "-n", K8S_NAMESPACE, K8S_POD, "--",
            *pg_cmd(
                "pg_dump",
                "--username", PG_USER,
                "--no-password",
                "--format", BACKUP_FORMAT,
                db_name,
            ),
        ]
        with output_path.open("wb") as f:
            subprocess.run(cmd, stdout=f, check=True)

    return output_path


def main() -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_dir = Path(BACKUP_DIR)
    backup_dir.mkdir(parents=True, exist_ok=True)

    log.info("PostgreSQL backup started")
    log.info("  Pod       : %s/%s", K8S_NAMESPACE, K8S_POD)
    log.info("  User      : %s",    PG_USER)
    log.info("  Format    : %s",    BACKUP_FORMAT)
    log.info("  Output dir: %s",    backup_dir.resolve())

    try:
        databases = list_databases()
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
            path = backup_database(db, backup_dir, timestamp)
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
