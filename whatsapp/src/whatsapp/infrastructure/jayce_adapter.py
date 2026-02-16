"""JayceAIAdapter — AIProvider implementation backed by jayce.

Consumes jayce's PUBLIC API only (AgentService, AgentResponse).
No internal jayce imports.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..domain.ports import AIProvider

if TYPE_CHECKING:
    from jayce import AgentService
    from langgraph.graph.state import CompiledStateGraph


class JayceAIAdapter(AIProvider):
    """AI provider backed by jayce's AgentService.

    Parameters
    ----------
    agent : AgentService
        The jayce agent orchestrator (already configured).
    graph : CompiledStateGraph
        The compiled LangGraph (obtained from ``agent.build_compiled_graph()``).
    """

    def __init__(self, agent: AgentService, graph: CompiledStateGraph) -> None:
        self._agent = agent
        self._graph = graph

    async def ask(self, text: str, *, thread_id: str) -> str:
        """Send a question to jayce and return the response content."""
        response = await self._agent.send_message(
            self._graph,
            text,
            thread_id=thread_id,
        )
        return response.content
