"""Tests for infrastructure checkpoint factory."""

from jayce.infrastructure.checkpointer.adapter import (
    MemoryCheckpointAdapter,
    PostgresCheckpointAdapter,
    SqliteCheckpointAdapter,
    create_checkpoint_adapter,
)

import pytest


class TestCheckpointFactory:
    """Tests for create_checkpoint_adapter factory."""

    def test_memory_adapter(self) -> None:
        adapter = create_checkpoint_adapter("memory")
        assert isinstance(adapter, MemoryCheckpointAdapter)

    def test_empty_dsn_returns_memory(self) -> None:
        adapter = create_checkpoint_adapter("")
        assert isinstance(adapter, MemoryCheckpointAdapter)

    def test_sqlite_adapter(self) -> None:
        adapter = create_checkpoint_adapter("sqlite:///test.db")
        assert isinstance(adapter, SqliteCheckpointAdapter)

    def test_postgres_adapter(self) -> None:
        adapter = create_checkpoint_adapter("postgres://user:pass@host/db")
        assert isinstance(adapter, PostgresCheckpointAdapter)

    def test_unsupported_dsn_raises(self) -> None:
        with pytest.raises(ValueError, match="Unsupported DSN"):
            create_checkpoint_adapter("mysql://host/db")
