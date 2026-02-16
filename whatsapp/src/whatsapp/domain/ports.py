"""Ports (abstract interfaces) — hexagonal architecture boundaries.

These ABCs define what the application layer NEEDS from the outside
world. Infrastructure adapters provide concrete implementations.

The domain NEVER imports concrete implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from .models import IncomingMessage, OutgoingMessage


class MessageGateway(ABC):
    """Port for messaging platform integration (driven adapter).

    The gateway connects to the platform, receives messages via a
    registered callback, and sends replies. Implementations may be
    neonize, Twilio, WPPConnect, or any other messaging backend.
    """

    @abstractmethod
    def on_message(self, callback: Callable[[IncomingMessage], None]) -> None:
        """Register a callback to be invoked for each incoming message."""
        ...

    @abstractmethod
    def send(self, message: OutgoingMessage) -> None:
        """Send a message through the platform."""
        ...

    @abstractmethod
    def connect(self) -> None:
        """Connect to the platform (may block the calling thread)."""
        ...


class AIProvider(ABC):
    """Port for AI backend integration.

    Any AI engine (jayce, OpenAI direct, Anthropic, etc.) can implement
    this port to provide conversational responses.
    """

    @abstractmethod
    async def ask(self, text: str, *, thread_id: str) -> str:
        """Send a question to the AI and return the response text."""
        ...


class ContactPolicy(ABC):
    """Port for contact authorization policy.

    Determines whether a sender is allowed to interact with the bot.
    Implementations can use allowlists, blocklists, or any other strategy.
    """

    @abstractmethod
    def is_allowed(self, sender_name: str, sender_id: str) -> bool:
        """Return True if the sender is authorized to interact."""
        ...
