"""LangChain LLM Adapter — implements LLMPort.

Encapsulates all LangChain-specific logic: model loading, tool binding,
and config overrides.

With langchain-ollama >= 1.0 and models that support tool calling
(e.g. llama3.1), tool calls are returned natively in AIMessage.tool_calls.
No manual JSON parsing or fallbacks are needed.
"""

import re
from collections.abc import Sequence
from typing import Any, TypedDict, Unpack, cast

from langchain.chat_models import BaseChatModel, init_chat_model
from langchain.tools import BaseTool
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from pydantic import BaseModel, ConfigDict

from ...domain.ports import LLMPort
from ...domain.prompts import DIRECT_REPLY_SYSTEM_PROMPT, SYSTEM_PROMPT

PAYLOAD_OR_KWARGS_MSG = "Provide either 'payload' or keyword arguments, not both."


class LangChainLLMAdapterPayloadTypedDict(TypedDict, total=False):
    """Keyword arguments for LangChainLLMAdapter; all fields optional."""

    model: str
    thinking_model: str
    provider: str
    base_url: str
    temperature: float
    max_tokens: int


class LangChainLLMAdapterPayload(BaseModel):
    """Payload for LangChainLLMAdapter. Validates dict or object (extra fields ignored)."""

    model: str = "llama3.1"
    thinking_model: str = "deepseek-r1"
    provider: str = "ollama"
    base_url: str = "http://127.0.0.1:11434"
    temperature: float = 0.2
    max_tokens: int = 4096

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class LangChainLLMAdapter(LLMPort):
    """Concrete LLM adapter using LangChain's ``init_chat_model``.

    Accepts either a single ``payload`` (dict or object with the expected attributes)
    or keyword arguments. Extra keys/attributes are ignored.
    """

    def __init__(
        self,
        *,
        payload: LangChainLLMAdapterPayload | dict[str, Any] | None = None,
        **kwargs: Unpack[LangChainLLMAdapterPayloadTypedDict],
    ) -> None:
        if payload is not None and kwargs:
            raise TypeError(PAYLOAD_OR_KWARGS_MSG)
        if payload is not None:
            validated = LangChainLLMAdapterPayload.model_validate(payload)
        elif kwargs:
            validated = LangChainLLMAdapterPayload.model_validate(kwargs)
        else:
            validated = LangChainLLMAdapterPayload()
        self._model = validated.model
        self._thinking_model = validated.thinking_model
        self._provider = validated.provider
        self._base_url = validated.base_url
        self._temperature = validated.temperature
        self._max_tokens = validated.max_tokens
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
                num_predict=self._max_tokens,
            ),
        )

    def _configured(self, *, model: str | None = None) -> BaseChatModel:
        """Return the LLM with model/provider config applied."""
        return cast(
            BaseChatModel,
            self._llm.with_config(
                config={
                    "configurable": {
                        "model": model or self._model,
                        "model_provider": self._provider,
                    }
                }
            ),
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

        # More robust and modern: type-safe, precompiled regex, concise, handles edge cases
        think_tag_pattern = re.compile(r"<think>(.*?)</think>", re.DOTALL)

        def extract_thinking(content: str | list[str | dict[Any, Any]]) -> tuple[str, list[str]]:
            """Extract <think>...</think> traces; return cleaned content and list of traces."""
            if not isinstance(content, str) or "<think>" not in content:
                return content if isinstance(content, str) else "", []
            thinking = think_tag_pattern.findall(content)
            cleaned = think_tag_pattern.sub("", content).strip()
            return cleaned, thinking

        clean_content, thinking_traces = extract_thinking(raw_content)

        return AIMessage(
            content=clean_content,
            response_metadata=result.response_metadata or {},
            usage_metadata=result.usage_metadata,
            additional_kwargs={
                **(result.additional_kwargs or {}),
                "thinking": "\n\n".join(t.strip() for t in thinking_traces)
                if thinking_traces
                else None,
            },
        )
