"""
Configuration schemas for Jayce AI Engine.

Uses Pydantic V2 for validation and sensible defaults (KISS principle).
"""

from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ToolConfig(BaseModel):
    """Configuration for external tools."""

    tavily_api_key: str | None = Field(
        default_factory=lambda: os.getenv("TAVILY_API_KEY"),
        description="API key for Tavily search. Falls back to TAVILY_API_KEY env var.",
    )
    tavily_max_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of search results to return.",
    )
    tavily_topic: Literal["general", "news"] = Field(
        default="general",
        description="Topic for Tavily search.",
    )
    enable_search: bool = Field(
        default=True,
        description="Whether to enable web search tool.",
    )


class JayceConfig(BaseModel):
    """
    Main configuration for Jayce AI Assistant.

    Implements sensible defaults following KISS principle.
    All configuration can be overridden via constructor or environment variables.

    Example:
        # Use all defaults (Ollama llama3.1)
        config = JayceConfig()

        # Custom model
        config = JayceConfig(model_name="openai:gpt-4o")

        # Custom everything
        config = JayceConfig(
            model_name="anthropic:claude-3-5-sonnet",
            system_prompt="You are a coding assistant.",
            temperature=0.7,
        )
    """

    model_config = {"extra": "forbid", "validate_default": True}

    # LLM Configuration
    model_name: str = Field(
        default="ollama:llama3.1",
        description=(
            "Model identifier in format 'provider:model'. "
            "Supported providers: ollama, openai, anthropic, google."
        ),
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for the model.",
    )
    max_tokens: int | None = Field(
        default=None,
        description="Maximum tokens in response. None means model default.",
    )

    # System Prompt
    system_prompt: str = Field(
        default=(
            "You are a helpful assistant. When you need current information, events, or facts "
            "from the web, use the search tool. Prefer answering from search results when the user "
            "asks about recent or external information. "
            "Always format your response in markdown."
        ),
        description="System prompt that defines the assistant's behavior.",
    )

    # Tool Configuration
    tools: ToolConfig = Field(
        default_factory=ToolConfig,
        description="Configuration for external tools.",
    )

    # Memory Configuration
    enable_memory: bool = Field(
        default=True,
        description="Whether to enable conversation memory.",
    )
    thread_id: str | None = Field(
        default=None,
        description="Thread ID for conversation persistence. Auto-generated if None.",
    )

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """Validate model name format."""
        if ":" not in v:
            msg = (
                f"Invalid model_name format: '{v}'. "
                "Expected format: 'provider:model' (e.g., 'ollama:llama3.1', 'openai:gpt-4o')"
            )
            raise ValueError(msg)
        return v

    @property
    def provider(self) -> str:
        """Extract provider from model_name."""
        return self.model_name.split(":")[0]

    @property
    def model(self) -> str:
        """Extract model from model_name."""
        return self.model_name.split(":", 1)[1]
