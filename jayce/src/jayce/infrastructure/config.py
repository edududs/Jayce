"""Application configuration via Pydantic Settings.

Loads from .env with path resolution. This is an infrastructure concern
because it deals with environment variables and file I/O.
"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_file() -> str | None:
    """Find .env by walking up from cwd. Returns first path that exists, or None."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        env_path = parent / ".env"
        if env_path.is_file():
            return str(env_path)
    return None


_env_file = _resolve_env_file()


class JayceSettings(BaseSettings):
    """Settings loaded from environment and .env. Validated at bootstrap."""

    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_dsn: str = Field(
        ...,
        description="Database connection string (e.g. sqlite:///path/to/jayce.db or postgres://...)",
    )

    tavily_api_key: str | None = Field(
        default=None,
        description="Tavily search API key (optional; Tavily tool is disabled when unset).",
    )


def load_settings(env_file: str | Path | None = None) -> JayceSettings:
    """Load and validate settings. Use explicit env_file to override auto-discovery."""
    kwargs = {}
    if env_file is not None:
        kwargs["_env_file"] = str(env_file)
    return JayceSettings(**kwargs)
