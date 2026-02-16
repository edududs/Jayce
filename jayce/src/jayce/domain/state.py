"""Agent state — the core data structure flowing through the LangGraph."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Annotated

from langgraph.graph.message import BaseMessage, add_messages


@dataclass(slots=True, frozen=True)
class State:
    messages: Annotated[Sequence[BaseMessage], add_messages]
