import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import psycopg

DEFAULT_DIR = Path(__file__).parent / "migrations"
LOCK_ID = 727_001

MIGRATION_PATTERN = re.compile(r"^(\d{4})_(.+)\.sql$")


class MigrationError(Exception):
    pass


class ChecksumMismatchError(MigrationError):
    pass


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    path: Path
    checksum: str


@dataclass(frozen=True)
class MigrationResult:
    version: int
    name: str
    status: Literal["applied", "skipped"]


def discover(directory: Path) -> list[Migration]:
    migrations: list[Migration] = []
    seen_versions: set[int] = set()

    for path in sorted(directory.glob("*.sql")):
        match = MIGRATION_PATTERN.fullmatch(path.name)

        if match is None:
            raise MigrationError(f"Invalid migration filename: {path.name}. Expected NNNN_name.sql")

        version = int(match.group(1))
        name = match.group(2)

        if version in seen_versions:
            raise MigrationError(f"Duplicate migration version {version}: {path.name}")

        seen_versions.add(version)

        checksum = hashlib.sha256(path.read_bytes()).hexdigest()

        migrations.append(
            Migration(
                version=version,
                name=name,
                path=path,
                checksum=checksum,
            )
        )

    return sorted(migrations, key=lambda migration: migration.version)


def run_migrations(
    database_url: str,
    directory: Path = DEFAULT_DIR,
) -> list[MigrationResult]:
    migrations = discover(directory)
    results: list[MigrationResult] = []

    with psycopg.connect(database_url, autocommit=True) as conn:
        conn.execute("SELECT pg_advisory_lock(%s)", (LOCK_ID,))

        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    filename TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )

            applied = {
                version: checksum
                for version, checksum in conn.execute(
                    "SELECT version, checksum FROM schema_migrations"
                ).fetchall()
            }

            for migration in migrations:
                if migration.version in applied:
                    if applied[migration.version] != migration.checksum:
                        raise ChecksumMismatchError(
                            f"Migration {migration.path.name} has changed after being applied"
                        )

                    results.append(
                        MigrationResult(
                            version=migration.version,
                            name=migration.name,
                            status="skipped",
                        )
                    )
                    continue

                with conn.transaction():
                    conn.execute(migration.path.read_bytes())

                    conn.execute(
                        """
                        INSERT INTO schema_migrations
                            (version, filename, checksum)
                        VALUES (%s, %s, %s)
                        """,
                        (
                            migration.version,
                            migration.path.name,
                            migration.checksum,
                        ),
                    )

                results.append(
                    MigrationResult(
                        version=migration.version,
                        name=migration.name,
                        status="applied",
                    )
                )

        finally:
            conn.execute(
                "SELECT pg_advisory_unlock(%s)",
                (LOCK_ID,),
            )

    return results
