"""
Jayce Factory - High-cohesion facade for the AI Engine.

This is the OFFICIAL entry point for consuming Jayce as a library.
Implements dependency injection with sensible defaults (KISS principle).

Usage:
    from jayce import create_assistant, JayceConfig

    # Simple usage with defaults
    assistant = create_assistant()
    response = assistant.chat("Hello!")

    # Custom configuration
    config = JayceConfig(
        model_name="openai:gpt-4o",
        temperature=0.5,
    )
    assistant = create_assistant(config)
"""

from __future__ import annotations

import threading
import uuid
from typing import TYPE_CHECKING

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from langchain_tavily import TavilySearch
from langgraph.graph.state import CompiledStateGraph, RunnableConfig

from jayce.core.graph import build_agent_graph
from jayce.schemas.config import JayceConfig

if TYPE_CHECKING:
    pass


class JayceAssistant:
    """
    High-level facade for the Jayce AI Assistant.

    This class provides a clean, simple API for interacting with the
    underlying LangGraph agent. It handles:
    - Model initialization
    - Tool setup
    - Conversation threading
    - Response extraction

    Example:
        assistant = JayceAssistant(JayceConfig())
        response = assistant.chat("What's the latest news?")
        print(response)
    """

    def __init__(
        self,
        config: JayceConfig | None = None,
        *,
        custom_tools: list[BaseTool] | None = None,
    ) -> None:
        """
        Initialize the Jayce Assistant.

        Args:
            config: Configuration object. Uses defaults if None.
            custom_tools: Optional list of custom tools to use instead of defaults.
        """
        self.config = config or JayceConfig()
        self._graph: CompiledStateGraph | None = None
        self._custom_tools = custom_tools
        self._thread_id = self.config.thread_id or str(uuid.uuid4())

    @property
    def graph(self) -> CompiledStateGraph:
        """Lazy initialization of the agent graph."""
        if self._graph is None:
            self._graph = self._build_graph()
        return self._graph

    def _build_graph(self) -> CompiledStateGraph:
        """Build the agent graph with current configuration."""
        # Initialize the LLM
        model = init_chat_model(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        # Setup tools
        tools = self._custom_tools or self._create_default_tools()

        # Build and return the graph
        return build_agent_graph(
            model=model,
            tools=tools,
            system_prompt=self.config.system_prompt,
            checkpointer=None,  # Uses InMemorySaver by default
        )

    def _create_default_tools(self) -> list[BaseTool]:
        """Create the default tool set based on configuration."""
        tools: list[BaseTool] = []

        if self.config.tools.enable_search and self.config.tools.tavily_api_key:
            tavily = TavilySearch(
                max_results=self.config.tools.tavily_max_results,
                topic=self.config.tools.tavily_topic,
            )
            tools.append(tavily)

        return tools

    @property
    def runnable_config(self) -> RunnableConfig:
        """Get the runnable config for graph invocation."""
        return RunnableConfig(
            configurable={"thread_id": self._thread_id},
        )

    def chat(self, message: str) -> str:
        """
        Send a message and get a response.

        This is the main entry point for conversation.

        Args:
            message: The user's message.

        Returns:
            The assistant's response as a string.
        """
        human_message = HumanMessage(content=message)
        result = self.graph.invoke(
            {"messages": [human_message]},
            config=self.runnable_config,
        )

        # Extract the final response
        if result["messages"]:
            last_content = result["messages"][-1].content
            return str(last_content) if last_content else ""
        return ""

    async def achat(self, message: str) -> str:
        """
        Async version of chat.

        Args:
            message: The user's message.

        Returns:
            The assistant's response as a string.
        """
        human_message = HumanMessage(content=message)
        result = await self.graph.ainvoke(
            {"messages": [human_message]},
            config=self.runnable_config,
        )

        if result["messages"]:
            last_content = result["messages"][-1].content
            return str(last_content) if last_content else ""
        return ""

    def reset(self) -> None:
        """Reset the conversation by generating a new thread ID."""
        self._thread_id = str(uuid.uuid4())

    def set_thread(self, thread_id: str) -> None:
        """
        Set a specific thread ID for conversation persistence.

        Args:
            thread_id: The thread ID to use.
        """
        self._thread_id = thread_id


def create_assistant(
    config: JayceConfig | None = None,
    *,
    custom_tools: list[BaseTool] | None = None,
) -> JayceAssistant:
    """
    Factory function to create a Jayce Assistant.

    This is the recommended way to instantiate the assistant.

    Args:
        config: Optional configuration. Uses sensible defaults if None.
        custom_tools: Optional custom tools to override defaults.

    Returns:
        Configured JayceAssistant instance.

    Example:
        # With defaults (Ollama llama3.1)
        assistant = create_assistant()

        # With custom model
        from jayce import JayceConfig
        config = JayceConfig(model_name="openai:gpt-4o")
        assistant = create_assistant(config)

        # Use it
        response = assistant.chat("What is LangGraph?")
    """
    return JayceAssistant(config=config, custom_tools=custom_tools)
