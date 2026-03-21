"""Agent Service — the main orchestrator (application use case).

This is the primary entry point for consumers of the Jayce library.
It receives all dependencies through constructor injection (ports)
and provides a clean API for sending messages and getting responses.

Design:
- Depends only on domain ports (LLMPort, CheckpointPort, ToolRegistryPort)
- Builds LangGraph nodes as thin wrappers around ports
- Exposes ``send_message()`` for single-turn interactions
- Exposes ``build_compiled_graph()`` for consumers needing the raw graph
"""

from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.runtime import Runtime
from rich import print

from ..domain.context import Context
from ..domain.ports import CheckpointPort, LLMPort, ToolRegistryPort
from ..domain.routing import RoutingPolicy
from ..domain.state import State
from .graph_builder import build_graph


@dataclass(frozen=True, slots=True)
class AgentResponse:
    """Structured response from the agent."""

    content: str
    model_name: str
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    duration_sec: float | None
    thinking: str | None = None


def _extract_response(message: AIMessage) -> AgentResponse:
    """Extract a structured AgentResponse from an AIMessage."""
    meta = message.response_metadata
    duration_sec = None
    if total_ns := meta.get("total_duration"):
        duration_sec = total_ns / 1e9

    usage = getattr(message, "usage_metadata", None) or {}
    in_t = usage.get("input_tokens") or meta.get("prompt_eval_count")
    out_t = usage.get("output_tokens") or meta.get("eval_count")
    total_t = usage.get("total_tokens") or meta.get("total_tokens")

    # Extract thinking trace if present (from deepseek-r1)
    additional = getattr(message, "additional_kwargs", {}) or {}
    thinking = additional.get("thinking")

    return AgentResponse(
        content=message.text,
        model_name=meta.get("model", ""),
        input_tokens=in_t,
        output_tokens=out_t,
        total_tokens=total_t,
        duration_sec=duration_sec,
        thinking=thinking,
    )


class AgentService:
    """Main agent orchestrator — composes LangGraph from injected ports.

    Example usage::

        llm = LangChainLLMAdapter(model="llama3.1", provider="ollama")
        tools = LangChainToolRegistryAdapter(settings)
        checkpoint = SqliteCheckpointAdapter(db_dsn)
        agent = AgentService(llm=llm, tools=tools, checkpoint=checkpoint)

        async with agent.build_compiled_graph() as graph:
            response = await agent.send_message(graph, "Hello!", thread_id="1")
    """

    def __init__(
        self,
        llm: LLMPort,
        tools: ToolRegistryPort,
        checkpoint: CheckpointPort,
    ) -> None:
        self._llm = llm
        self._tools = tools
        self._checkpoint = checkpoint

    def _make_direct_llm_node(self) -> Callable[[State, Runtime[Context]], State]:
        """Create the direct_llm node (no tools, for healthchecks)."""
        llm = self._llm

        def direct_llm(state: State, runtime: Runtime[Context]) -> State:  # noqa: ARG001
            print("[bold cyan]direct_llm:[/] [green]no tools, direct reply[/]")
            result = llm.invoke_direct(state.messages)
            return State(messages=[result])

        return direct_llm

    def _make_call_llm_node(self) -> Callable[[State, Runtime[Context]], State]:
        """Create the call_llm node (with tools).

        When ``ctx.thinking`` is True, a two-model strategy is used:
        1. llama3.1 decides whether tools are needed (it supports tool calling)
        2. If the answer is final (no tool calls), deepseek-r1 re-processes
           the full conversation for a deeply reasoned response
        """
        llm = self._llm
        tools_list = self._tools.get_tools()

        def call_llm(state: State, runtime: Runtime[Context]) -> State:
            ctx = runtime.context
            print(f"[bold cyan]call_llm:[/] [green]thinking={ctx.thinking}[/]")

            # Step 1: always use the standard model for tool-calling decisions
            result = llm.invoke(state.messages, tools=tools_list)

            # If there are tool calls, return as-is (tools node will execute them)
            if result.tool_calls:
                print("[bold cyan]call_llm:[/] [green]tool calls detected, routing to tools[/]")
                return State(messages=[result])

            # Step 2: final answer — if thinking mode, re-invoke with reasoning model
            if ctx.thinking:
                print("[bold cyan]call_llm:[/] [magenta]thinking mode → deepseek-r1[/]")
                result = llm.invoke_thinking(state.messages)

            return State(messages=[result])

        return call_llm

    def _make_tool_node(self) -> ToolNode:
        """Create the tools execution node."""
        return ToolNode(tools=self._tools.get_tools())

    def build_compiled_graph(
        self,
    ) -> AbstractAsyncContextManager[CompiledStateGraph[State, Context, State, State]]:
        """
        Asynchronously builds and returns the compiled graph as an async context manager.

        Example
        -------
        Usage::

            async with agent.build_compiled_graph() as graph:
                result = await graph.ainvoke(...)

        Returns
        -------
        AsyncContextManager[CompiledStateGraph]
            An async context manager that yields the compiled LangGraph ready for invocation.
        """
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def _graph_ctx() -> AsyncGenerator[CompiledStateGraph[State, Context, State, State]]:
            async with self._checkpoint.get_saver() as saver:
                graph = build_graph(
                    checkpointer=saver,
                    direct_llm_node=self._make_direct_llm_node(),
                    call_llm_node=self._make_call_llm_node(),
                    tool_node=self._make_tool_node(),
                    route_fn=RoutingPolicy.route,
                )
                yield graph

        return _graph_ctx()

    @staticmethod
    async def send_message(
        graph: CompiledStateGraph,
        message: str,
        *,
        thread_id: str = "1",
        thinking: bool = False,
    ) -> AgentResponse:
        """Send a message through the agent graph and return a structured response.

        Parameters
        ----------
        graph : CompiledStateGraph
            The compiled graph (obtained from ``build_compiled_graph``).
        message : str
            User message text.
        thread_id : str
            Conversation thread identifier.
        thinking : bool
            Whether the model should engage in deeper reasoning.

        Returns
        -------
        AgentResponse
            Structured response with content, metadata, and usage stats.
        """
        from langgraph.graph.state import RunnableConfig

        context = Context(thinking=thinking)
        config = RunnableConfig(configurable={"thread_id": thread_id})
        current_state = State(messages=[HumanMessage(message)])

        result = await graph.ainvoke(current_state, config=config, context=context)  # pyright: ignore[reportArgumentType]

        last_message = result["messages"][-1]
        if isinstance(last_message, AIMessage):
            return _extract_response(last_message)

        return AgentResponse(
            content=last_message.text
            if hasattr(last_message, "text")
            else str(last_message.content),
            model_name="",
            input_tokens=None,
            output_tokens=None,
            total_tokens=None,
            duration_sec=None,
        )
