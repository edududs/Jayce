"""Routing policy — deterministic routing logic extracted from nodes.py.

Pure domain logic with ZERO infrastructure dependencies.
"""

from langchain_core.messages import HumanMessage

from .prompts import HEALTHCHECK_PHRASES
from .state import State


def _normalize(content: str) -> str:
    return content.strip().lower() if content else ""


class RoutingPolicy:
    """Determines which graph node should process the message.

    Routes to ``direct_llm`` (no tools) for known healthcheck/greeting phrases.
    Everything else goes to ``call_llm`` (with tools).
    This is deterministic — no extra LLM call required.
    """

    DIRECT_NODE = "direct_llm"
    TOOLS_NODE = "call_llm"

    @staticmethod
    def should_route_direct(state: State) -> bool:
        """Return True when the message is a simple healthcheck/greeting."""
        if not state.messages:
            return False
        last = state.messages[-1]
        if not isinstance(last, HumanMessage):
            return False
        content = getattr(last, "content", "") or ""
        if isinstance(content, list):
            return False
        return _normalize(content) in HEALTHCHECK_PHRASES

    @classmethod
    def route(cls, state: State, *_: object, **__: object) -> str:
        """Conditional edge from START: direct_llm vs call_llm."""
        return cls.DIRECT_NODE if cls.should_route_direct(state) else cls.TOOLS_NODE
