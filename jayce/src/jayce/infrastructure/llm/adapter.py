"""LangChain LLM Adapter — implements LLMPort.

Encapsulates all LangChain-specific logic: model loading, tool binding,
and config overrides.

With langchain-ollama >= 1.0 and models that support tool calling
(e.g. llama3.1), tool calls are returned natively in AIMessage.tool_calls.
No manual JSON parsing or fallbacks are needed.
"""

import re
from collections.abc import Sequence
from typing import cast

from langchain.chat_models import BaseChatModel, init_chat_model
from langchain.tools import BaseTool
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage

from ...domain.ports import LLMPort
from ...domain.prompts import DIRECT_REPLY_SYSTEM_PROMPT, SYSTEM_PROMPT


class LangChainLLMAdapter(LLMPort):
    """Concrete LLM adapter using LangChain's ``init_chat_model``.

    Parameters
    ----------
    model : str
        Model name for general use (e.g. ``"llama3.1"``).
    thinking_model : str
        Model name for deep reasoning (e.g. ``"deepseek-r1"``).
    provider : str
        Model provider (e.g. ``"ollama"``).
    base_url : str
        Base URL for the model API.
    temperature : float
        Sampling temperature.
    """

    def __init__(
        self,
        model: str = "llama3.1",
        thinking_model: str = "deepseek-r1",
        provider: str = "ollama",
        base_url: str = "http://127.0.0.1:11434",
        temperature: float = 0.2,
    ) -> None:
        self._model = model
        self._thinking_model = thinking_model
        self._provider = provider
        self._base_url = base_url
        self._temperature = temperature
        self._llm = self._build_llm()

    def _build_llm(self) -> BaseChatModel:
        return cast(
            "BaseChatModel",
            init_chat_model(
                model=self._model,
                model_provider=self._provider,
                base_url=self._base_url,
                temperature=self._temperature,
                configurable_fields="any",
            ),
        )

    def _configured(self, *, model: str | None = None) -> BaseChatModel:
        """Return the LLM with model/provider config applied."""
        return self._llm.with_config(
            config={
                "configurable": {
                    "model": model or self._model,
                    "model_provider": self._provider,
                }
            }
        )

    def invoke(
        self,
        messages: Sequence[BaseMessage],
        tools: list[BaseTool],
    ) -> AIMessage:
        """Invoke LLM with tools bound.

        With langchain-ollama >= 1.0, tool calls are returned natively
        in ``AIMessage.tool_calls`` — no manual parsing needed.
        """
        llm_with_tools = self._configured().bind_tools(tools)
        system = SystemMessage(content=SYSTEM_PROMPT)
        return llm_with_tools.invoke([system, *messages])

    def invoke_direct(self, messages: Sequence[BaseMessage]) -> AIMessage:
        """Invoke LLM without tools (direct_llm node for healthchecks)."""
        system = SystemMessage(content=DIRECT_REPLY_SYSTEM_PROMPT)
        return self._configured().invoke([system, *messages])

    def invoke_thinking(self, messages: Sequence[BaseMessage]) -> AIMessage:
        """Invoke the reasoning model (deepseek-r1) for deep thinking.

        The model outputs reasoning in ``<think>...</think>`` tags.
        We strip those from the final content and store them separately
        in ``additional_kwargs['thinking']`` for optional display.
        """
        system = SystemMessage(content=SYSTEM_PROMPT)
        result = self._configured(model=self._thinking_model).invoke([system, *messages])

        raw_content = result.content or ""
        thinking_traces: list[str] = []
        clean_content = raw_content

        if "<think>" in raw_content:
            pattern = re.compile(r"<think>(.*?)</think>", re.DOTALL)
            thinking_traces = pattern.findall(raw_content)
            clean_content = pattern.sub("", raw_content).strip()

        return AIMessage(
            content=clean_content,
            response_metadata=result.response_metadata or {},
            usage_metadata=result.usage_metadata,
            additional_kwargs={
                **(result.additional_kwargs or {}),
                "thinking": "\n\n".join(t.strip() for t in thinking_traces) if thinking_traces else None,
            },
        )
