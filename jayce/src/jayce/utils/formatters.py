"""
Formatting utilities for Jayce.

Contains helper functions to format various data types for LLM consumption.
"""

from __future__ import annotations

import json
from typing import Any


def format_search_result(raw: dict[str, Any]) -> str:
    """
    Format raw search results into a readable string for the LLM.

    Args:
        raw: Raw search result dictionary from Tavily or similar.

    Returns:
        Formatted string with search results.
    """
    results = raw.get("results") or []
    items = results if isinstance(results, list) else []

    parts = []
    for result in items:
        if not isinstance(result, dict):
            continue

        title = result.get("title", "No title")
        url = result.get("url", "")
        content = result.get("content", "")

        parts.append(f"- **{title}**\n  URL: {url}\n  {content}")

    if not parts:
        # Fallback to JSON if no structured results
        return json.dumps(raw, ensure_ascii=False, indent=2)

    return "\n\n".join(parts)


def format_error(error: Exception, context: str | None = None) -> str:
    """
    Format an exception into a user-friendly error message.

    Args:
        error: The exception that occurred.
        context: Optional context about what was being attempted.

    Returns:
        Formatted error message.
    """
    error_type = type(error).__name__
    error_msg = str(error)

    if context:
        return f"Error during {context}: [{error_type}] {error_msg}"
    return f"Error: [{error_type}] {error_msg}"
