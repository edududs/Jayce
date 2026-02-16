"""Checkpoint adapters — implements CheckpointPort.

Provides factory functions for different checkpoint backends:
- In-memory (development)
- SQLite (local persistence)
- PostgreSQL (production)
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from ...domain.ports import CheckpointPort


class MemoryCheckpointAdapter(CheckpointPort):
    """In-memory checkpoint adapter for development/testing."""

    @asynccontextmanager
    async def get_saver(self) -> AsyncGenerator[InMemorySaver]:
        yield InMemorySaver()


class SqliteCheckpointAdapter(CheckpointPort):
    """SQLite checkpoint adapter for local persistence."""

    def __init__(self, db_dsn: str) -> None:
        self._db_dsn = db_dsn

    @asynccontextmanager
    async def get_saver(self) -> AsyncGenerator[AsyncSqliteSaver]:
        # Explicitly manage aiosqlite connection to control thread affinity
        # and prevent implicit re-connection attempts.
        import aiosqlite
        
        # Determine path from DSN (sqlite:///path or just path)
        path = self._db_dsn.replace("sqlite:///", "") if "://" in self._db_dsn else self._db_dsn
        
        async with aiosqlite.connect(path, check_same_thread=False) as conn:
            saver = AsyncSqliteSaver(conn)
            # Setup tables if needed (AsyncSqliteSaver might not do it automatically if passed a conn)
            await saver.setup()
            yield saver


class PostgresCheckpointAdapter(CheckpointPort):
    """PostgreSQL checkpoint adapter for production."""

    def __init__(self, db_dsn: str) -> None:
        self._db_dsn = db_dsn

    @asynccontextmanager
    async def get_saver(self) -> AsyncGenerator[AsyncPostgresSaver]:
        async with AsyncPostgresSaver.from_conn_string(self._db_dsn) as saver:
            await saver.setup()
            yield saver


def create_checkpoint_adapter(db_dsn: str) -> CheckpointPort:
    """Factory: create the appropriate checkpoint adapter based on the DSN.

    - ``sqlite:///...`` → SqliteCheckpointAdapter
    - ``postgres://...`` → PostgresCheckpointAdapter
    - ``memory`` or empty → MemoryCheckpointAdapter
    - bare file path (e.g. ``/abs/path/to/db``) → SqliteCheckpointAdapter
      (bootstrap resolves sqlite DSNs to absolute paths)
    """
    if not db_dsn or db_dsn.strip() == "memory":
        return MemoryCheckpointAdapter()
    if db_dsn.startswith("sqlite"):
        return SqliteCheckpointAdapter(db_dsn)
    if db_dsn.startswith("postgres"):
        return PostgresCheckpointAdapter(db_dsn)
    # Bootstrap resolves sqlite:///... → bare absolute path
    if db_dsn.startswith("/") or db_dsn.endswith(".db"):
        return SqliteCheckpointAdapter(db_dsn)
    msg = f"Unsupported DSN scheme: {db_dsn!r}"
    raise ValueError(msg)
