"""Domain models — platform-agnostic message representations.

These dataclasses carry data between layers without any dependency
on messaging platform libraries (neonize, Twilio, etc.).
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IncomingMessage:
    """A message received from any messaging platform."""

    text: str
    chat_id: str
    sender_id: str
    sender_name: str
    is_from_me: bool


@dataclass(frozen=True, slots=True)
class OutgoingMessage:
    """A message to send back through the messaging platform."""

    text: str
    chat_id: str
