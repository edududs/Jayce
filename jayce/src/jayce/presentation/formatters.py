"""Response formatters — presentation utilities for agent responses.

Extracted from the old main.py for isolation and reusability.
"""

from ..application.agent_service import AgentResponse


def format_response_footer(response: AgentResponse) -> str:
    """Format the footer line with duration and token usage.

    Returns
    -------
    str
        Formatted footer string, e.g. ``"2.34s | tokens: in=100, out=50, total=150"``
        or empty string if no metadata is available.
    """
    parts: list[str] = []

    if response.duration_sec is not None:
        parts.append(f"{response.duration_sec:.2f}s")

    token_parts: list[str] = []
    if response.input_tokens is not None:
        token_parts.append(f"in={response.input_tokens}")
    if response.output_tokens is not None:
        token_parts.append(f"out={response.output_tokens}")
    if response.total_tokens is not None:
        token_parts.append(f"total={response.total_tokens}")

    if token_parts:
        parts.append(f"tokens: {', '.join(token_parts)}")

    return " | ".join(parts)
