"""
Tool execution node for the Jayce agent graph.

This module handles the execution of tools called by the LLM.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool

from jayce.schemas.state import AgentState
from jayce.utils.formatters import format_search_result

if TYPE_CHECKING:
    from collections.abc import Callable


def create_tool_node(
    tools: list[BaseTool],
) -> Callable[[AgentState], AgentState]:
    """
    Factory function to create a tool execution node.

    Args:
        tools: List of tools available to the agent.

    Returns:
        A callable node function that executes tool calls.
    """
    tools_by_name = {tool.name: tool for tool in tools}

    def execute_tools(state: AgentState) -> AgentState:
        """
        Execute tool calls from the last LLM message.

        Args:
            state: Current agent state with pending tool calls.

        Returns:
            Updated state with tool results appended.
        """
        last_message = state["messages"][-1]
        tool_calls = getattr(last_message, "tool_calls", None) or []
        result_messages = []

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool = tools_by_name.get(tool_name)

            if tool is None:
                observation = f"Error: Unknown tool '{tool_name}'"
            else:
                try:
                    raw_result = tool.invoke(tool_call.get("args") or {})
                    # Format search results for better readability
                    observation = (
                        format_search_result(raw_result)
                        if isinstance(raw_result, dict)
                        else str(raw_result)
                    )
                except Exception as e:  # noqa: BLE001
                    observation = f"Error executing tool '{tool_name}': {e}"

            result_messages.append(
                ToolMessage(
                    content=observation,
                    tool_call_id=tool_call["id"],
                )
            )

        return {"messages": result_messages}

    return execute_tools


def should_continue(state: AgentState) -> Literal["tool_node", "__end__"]:
    """
    Conditional edge function to determine next step.

    Checks if the last message contains tool calls that need execution.

    Args:
        state: Current agent state.

    Returns:
        "tool_node" if there are pending tool calls, "__end__" otherwise.
    """
    messages = state["messages"]
    if not messages:
        return "__end__"

    last_message = messages[-1]
    if getattr(last_message, "tool_calls", None):
        return "tool_node"

    return "__end__"
