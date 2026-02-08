"""
State schemas for LangGraph workflows.

Defines the state structure that flows through the graph nodes.
"""

from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph import add_messages
from langgraph.graph.message import BaseMessage


class AgentState(TypedDict):
    """
    State structure for the Jayce agent graph.

    This TypedDict defines what data flows between nodes in the LangGraph.
    The `add_messages` reducer handles message list concatenation automatically.

    Attributes:
        messages: List of conversation messages with automatic reduction.
    """

    messages: Annotated[list[BaseMessage], add_messages]


class AgentOutput(TypedDict):
    """Output structure from agent invocation."""

    messages: list[BaseMessage]
    final_response: str
