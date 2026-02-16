"""Jayce — AI Engine with Hexagonal Architecture.

Public API
----------
- ``JayceSettings``: Configuration loaded from .env
- ``AgentService``: Main agent orchestrator (use case)
- ``AgentResponse``: Structured response dataclass
- ``bootstrap``: Configuration & environment bootstrap
- ``create_agent_service``: Composition root factory
- ``build_graph``: LangGraph builder (for LangGraph Studio / advanced usage)

Hexagonal layers:
    domain/          — Core entities, ports (ABCs), routing policy
    application/     — Use cases (AgentService, bootstrap, graph_builder)
    infrastructure/  — Adapters (LLM, checkpointer, tools, config)
    presentation/    — Driving adapters (CLI, formatters)
"""

from .application.agent_service import AgentResponse, AgentService
from .application.bootstrap import bootstrap
from .application.graph_builder import build_graph
from .infrastructure.config import JayceSettings
from .presentation.cli import create_agent_service

__all__ = [
    "AgentResponse",
    "AgentService",
    "JayceSettings",
    "bootstrap",
    "build_graph",
    "create_agent_service",
]
