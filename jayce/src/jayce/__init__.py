"""
Jayce - AI Engine for Assistente.

A pure Python library for AI orchestration using LangGraph.
This package is framework-agnostic and has ZERO Django dependencies.

Usage:
    from jayce import create_assistant, JayceConfig

    # With defaults (uses Ollama llama3.1)
    assistant = create_assistant()
    
    # With custom config
    config = JayceConfig(model_name="openai:gpt-4o")
    assistant = create_assistant(config)
    
    # Run a conversation
    response = assistant.chat("What's the weather like?")
"""

from jayce.factory import JayceAssistant, create_assistant
from jayce.schemas.config import JayceConfig
from jayce.schemas.state import AgentState

__version__ = "0.1.0"
__all__ = [
    "create_assistant",
    "JayceAssistant",
    "JayceConfig",
    "AgentState",
]
