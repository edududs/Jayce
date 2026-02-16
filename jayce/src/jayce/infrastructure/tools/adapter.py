"""Tool registry adapter — implements ToolRegistryPort.

Builds the list of available tools based on configuration.
Currently supports Tavily Search; extensible to any LangChain tool.
"""

from langchain.tools import BaseTool
from langchain_tavily import TavilySearch

from ...domain.ports import ToolRegistryPort
from ..config import JayceSettings


class LangChainToolRegistryAdapter(ToolRegistryPort):
    """Concrete tool registry using LangChain tools.

    Tools are built lazily on first access and cached.
    """

    def __init__(self, settings: JayceSettings) -> None:
        self._settings = settings
        self._tools: list[BaseTool] | None = None

    def _build_tools(self) -> list[BaseTool]:
        """Build tool list from settings."""
        tools: list[BaseTool] = []
        if self._settings.tavily_api_key:
            tools.append(
                TavilySearch(
                    tavily_api_key=self._settings.tavily_api_key,
                    max_results=10,
                    topic="general",
                )
            )
        return tools

    def get_tools(self) -> list[BaseTool]:
        """Return the list of available tools."""
        if self._tools is None:
            self._tools = self._build_tools()
        return self._tools

    def get_tool_names(self) -> set[str]:
        """Return the set of available tool names."""
        return {t.name for t in self.get_tools()}
