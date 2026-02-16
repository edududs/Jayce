"""Ports (abstract interfaces) — the hexagonal architecture boundaries.

These ABCs define what the domain/application layer NEEDS from the
outside world. The infrastructure layer provides concrete adapters.

Design principle: the domain NEVER imports concrete implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from langchain.tools import BaseTool
    from langchain_core.messages import AIMessage, BaseMessage
    from langgraph.checkpoint.base import BaseCheckpointSaver


class LLMPort(ABC):
    """Port for LLM interactions.

    Provides three invocation modes:
    - ``invoke``: with tools bound (for the main call_llm node)
    - ``invoke_direct``: without tools (for healthcheck/greeting replies)
    - ``invoke_thinking``: without tools, using a reasoning model (e.g. deepseek-r1)
    """

    @abstractmethod
    def invoke(
        self,
        messages: Sequence[BaseMessage],
        tools: list[BaseTool],
    ) -> AIMessage:
        """Invoke the LLM with tools bound."""
        ...

    @abstractmethod
    def invoke_direct(self, messages: Sequence[BaseMessage]) -> AIMessage:
        """Invoke the LLM without tools (direct reply mode)."""
        ...

    @abstractmethod
    def invoke_thinking(self, messages: Sequence[BaseMessage]) -> AIMessage:
        """Invoke a reasoning model (e.g. deepseek-r1) without tools.

        The model may include reasoning traces in ``<think>...</think>`` tags.
        """
        ...


class CheckpointPort(ABC):
    """Port for checkpoint/state persistence."""

    @abstractmethod
    def get_saver(self) -> AbstractAsyncContextManager[BaseCheckpointSaver]:
        """Return an async context manager yielding a checkpoint saver."""
        ...


class ToolRegistryPort(ABC):
    """Port for tool registration and discovery."""

    @abstractmethod
    def get_tools(self) -> list[BaseTool]:
        """Return the list of available tools."""
        ...

    @abstractmethod
    def get_tool_names(self) -> set[str]:
        """Return the set of available tool names."""
        ...
