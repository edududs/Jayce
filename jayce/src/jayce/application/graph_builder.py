"""LangGraph graph builder — pure composition of nodes and edges.

This module builds the StateGraph from domain routing policy and
application-level node functions. It does NOT import infrastructure
directly — all dependencies come through function parameters (DI).
"""

from collections.abc import Callable

from langgraph.constants import END, START
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.prebuilt.tool_node import ToolNode, tools_condition
from langgraph.pregel.main import BaseCheckpointSaver

from ..domain.context import Context
from ..domain.state import State


def build_graph(
    checkpointer: BaseCheckpointSaver,
    direct_llm_node: Callable[..., State],
    call_llm_node: Callable[..., State],
    tool_node: ToolNode,
    route_fn: Callable[..., str],
) -> CompiledStateGraph[State, Context, State, State]:
    """Build and compile the LangGraph StateGraph.

    Flow::

        START → [route_fn] → direct_llm | call_llm
          - direct_llm: no tools, for healthcheck/short messages → END
          - call_llm: with tools → [tools_condition] → tools | END
          - tools → call_llm (loop)

    Parameters
    ----------
    checkpointer : BaseCheckpointSaver
        State persistence backend.
    direct_llm_node : Callable
        Node for direct LLM replies (no tools).
    call_llm_node : Callable
        Node for LLM replies with tool access.
    tool_node : ToolNode
        Node for executing tool calls.
    route_fn : Callable
        Conditional routing function from START.
    """
    builder = StateGraph(
        state_schema=State,
        context_schema=Context,
        input_schema=State,
        output_schema=State,
    )

    builder.add_node("direct_llm", direct_llm_node)
    builder.add_node("call_llm", call_llm_node)
    builder.add_node("tools", tool_node)

    builder.add_conditional_edges(
        START, route_fn, {"direct_llm": "direct_llm", "call_llm": "call_llm"}
    )
    builder.add_edge("direct_llm", END)
    builder.add_conditional_edges("call_llm", tools_condition, ["tools", END])
    builder.add_edge("tools", "call_llm")

    return builder.compile(checkpointer=checkpointer)
