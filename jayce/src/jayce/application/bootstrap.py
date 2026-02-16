"""Bootstrap service — configuration validation and environment preparation.

Runs once at startup. Similar to Django's system checks before runserver.
"""

from pathlib import Path

from rich.console import Console

from ..infrastructure.config import JayceSettings, load_settings

console = Console()

_SQLITE_PREFIX = "sqlite:///"
_SQLITE_PREFIX_4 = "sqlite:////"


def _ensure_sqlite_path(db_dsn: str) -> Path | None:
    """Ensure parent directory of SQLite DB exists and file is created.

    Returns resolved absolute Path for sqlite DSN, None otherwise.
    """
    if not db_dsn.startswith(_SQLITE_PREFIX):
        return None
    if db_dsn.startswith(_SQLITE_PREFIX_4):
        path_str = db_dsn[len(_SQLITE_PREFIX_4) :]
    else:
        path_str = db_dsn[len(_SQLITE_PREFIX) :]
    path = Path(path_str).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch()
    return path


def _check_db_dsn(db_dsn: str) -> tuple[list[str], str | None]:
    """Validate DSN and prepare path. Returns (errors, resolved_dsn).

    For sqlite, resolved_dsn is the absolute file path
    (langgraph/aiosqlite expect path, not URI).
    For postgres, None (use original DSN).
    """
    errors: list[str] = []
    resolved_dsn: str | None = None
    if not db_dsn or not db_dsn.strip():
        errors.append("DB_DSN is empty")
        return (errors, None)
    if db_dsn.startswith("sqlite"):
        path = _ensure_sqlite_path(db_dsn)
        if path is not None:
            resolved_dsn = path.as_posix()
    elif not db_dsn.startswith("postgres"):
        errors.append("DB_DSN must be sqlite:///... or postgres://...")
    return (errors, resolved_dsn)


def bootstrap(env_file: str | Path | None = None) -> JayceSettings:
    """Load settings, validate config, prepare DB/paths. Call once before main()."""
    settings = load_settings(env_file=env_file)

    errors, resolved_dsn = _check_db_dsn(settings.db_dsn)
    if errors:
        for msg in errors:
            console.print(f"[red]Bootstrap error:[/red] {msg}")
        msg = "Bootstrap failed: invalid or missing DB configuration"
        raise RuntimeError(msg)

    if resolved_dsn is not None:
        settings = settings.model_copy(update={"db_dsn": resolved_dsn})

    console.print("[green]Bootstrap OK[/green] — config loaded, DB path ready")
    return settings
