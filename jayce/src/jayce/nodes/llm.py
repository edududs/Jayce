"""
LLM node for the Jayce agent graph.

This module contains the node that calls the language model.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage

from jayce.schemas.state import AgentState

if TYPE_CHECKING:
    from collections.abc import Callable


def create_llm_node(
    model: BaseChatModel,
    system_prompt: str,
) -> Callable[[AgentState], AgentState]:
    """
    Factory function to create an LLM node.

    This follows dependency injection pattern - the model and prompt
    are injected at creation time, making the node testable and flexible.

    Args:
        model: The language model to use (already bound with tools if needed).
        system_prompt: The system prompt to prepend to conversations.

    Returns:
        A callable node function compatible with LangGraph.
    """

    def call_llm(state: AgentState) -> AgentState:
        """
        Invoke the LLM with the current conversation state.

        Args:
            state: Current agent state with message history.

        Returns:
            Updated state with the LLM's response appended.
        """
        messages = [SystemMessage(content=system_prompt), *state["messages"]]
        response = model.invoke(messages)
        return {"messages": [response]}

    return call_llm
