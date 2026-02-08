"""
LangGraph workflow builder for Jayce.

This module constructs the agent graph with nodes for LLM calls and tool execution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from jayce.nodes.llm import create_llm_node
from jayce.nodes.tools import create_tool_node, should_continue
from jayce.schemas.state import AgentState

if TYPE_CHECKING:
    pass


def build_agent_graph(
    model: BaseChatModel,
    tools: list[BaseTool],
    system_prompt: str,
    checkpointer: BaseCheckpointSaver | None = None,
) -> CompiledStateGraph:
    """
    Build and compile the Jayce agent graph.

    This creates a ReAct-style agent that can:
    1. Call the LLM with conversation history
    2. Execute tools if the LLM requests them
    3. Loop back to LLM with tool results

    Args:
        model: The language model (will be bound with tools).
        tools: List of tools available to the agent.
        system_prompt: System prompt for the LLM.
        checkpointer: Optional checkpointer for conversation persistence.

    Returns:
        Compiled LangGraph ready for invocation.

    Graph Structure:
        START -> call_llm -> [should_continue] -> tool_node -> call_llm
                                              |-> END
    """
    # Bind tools to model
    model_with_tools = model.bind_tools(tools) if tools else model

    # Create nodes with dependency injection
    llm_node = create_llm_node(model_with_tools, system_prompt)
    tool_node = create_tool_node(tools)

    # Build the graph
    builder = StateGraph(
        AgentState,
        input_schema=AgentState,
        output_schema=AgentState,
    )

    # Add nodes
    builder.add_node("call_llm", llm_node)
    builder.add_node("tool_node", tool_node)

    # Add edges
    builder.add_edge(START, "call_llm")
    builder.add_conditional_edges(
        "call_llm",
        should_continue,
        ["tool_node", END],
    )
    builder.add_edge("tool_node", "call_llm")

    # Compile with optional checkpointer
    if checkpointer is None:
        checkpointer = InMemorySaver()

    return builder.compile(checkpointer=checkpointer)
