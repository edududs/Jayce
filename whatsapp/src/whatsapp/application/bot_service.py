"""BotService — the main application orchestrator.

Pure business logic: receives messages, checks authorization,
extracts AI triggers, calls AI, sends replies. Depends only on
abstract ports (MessageGateway, AIProvider, ContactPolicy).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Coroutine
from typing import Any

from ..domain.models import IncomingMessage, OutgoingMessage
from ..domain.ports import AIProvider, ContactPolicy, MessageGateway

logger = logging.getLogger(__name__)

IA_PREFIX: str = "/ia"

NO_QUESTION_REPLY: str = "Manda a pergunta junto, tipo: /ia qual o tempo?"

AI_NO_RESPONSE: str = "[IA não retornou texto]"


class BotService:
    """Application orchestrator — pure business logic.

    Any allowed contact can send ``/ia <pergunta>`` to have the question
    forwarded to the AI engine. The response is sent back in the same chat.

    The ``loop`` parameter is a running ``asyncio`` event loop (in a
    background thread). AI calls are dispatched to this loop via
    ``run_coroutine_threadsafe`` to avoid the ``aiosqlite`` "threads
    can only be started once" crash that happens with ``asyncio.run()``.

    Usage::

        bot = BotService(gateway=neonize, ai=jayce, contact_policy=allowlist, loop=loop)
        bot.start()  # blocks on gateway.connect()
    """

    def __init__(
        self,
        gateway: MessageGateway,
        ai: AIProvider,
        contact_policy: ContactPolicy,
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        self._gateway = gateway
        self._ai = ai
        self._contact_policy = contact_policy
        self._loop = loop
        # Register self as the message handler
        self._gateway.on_message(self._handle_message)
        logger.info("BotService initialized, message handler registered")

    def start(self) -> None:
        """Connect to the messaging platform (blocks)."""
        logger.info("BotService.start() — connecting gateway...")
        self._gateway.connect()

    def _run_async(self, coro: Coroutine[Any, Any, str]) -> str:
        """Run an async coroutine from a sync callback thread-safely.

        Uses the persistent event loop instead of asyncio.run() to
        avoid creating new loops (which breaks aiosqlite's thread).
        """
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)  # type: ignore[arg-type]
        return future.result(timeout=120)  # 2 min timeout for AI responses

    def _handle_message(self, msg: IncomingMessage) -> None:
        """Central message handler — dispatches based on content."""
        logger.debug(
            "_handle_message called",
            extra={
                "text": msg.text[:80],
                "sender_name": msg.sender_name,
                "sender_id": msg.sender_id,
                "chat_id": msg.chat_id,
                "is_from_me": msg.is_from_me,
            },
        )

        if msg.is_from_me:
            logger.debug("Skipping own message")
            return

        allowed = self._contact_policy.is_allowed(msg.sender_name, msg.sender_id)
        logger.debug(
            "Contact policy check",
            extra={
                "sender_name": msg.sender_name,
                "sender_id": msg.sender_id,
                "allowed": allowed,
            },
        )

        if not allowed:
            return

        # Log ALL messages from allowed contacts
        logger.info(
            "📩 Allowed message",
            extra={
                "sender": msg.sender_name,
                "chat_id": msg.chat_id,
                "text": msg.text,
            },
        )

        question = self._extract_ai_question(msg.text)
        logger.debug("AI trigger check", extra={"question": question})

        if question is None:
            return  # Not an /ia message, no auto-reply

        if not question:
            logger.info("Empty /ia question, sending hint")
            self._send_reply(msg.chat_id, NO_QUESTION_REPLY)
            return

        logger.info(
            "🤖 Forwarding to AI",
            extra={
                "sender": msg.sender_name,
                "question": question,
            },
        )

        # Ask AI via persistent event loop (safe for aiosqlite)
        try:
            reply = self._run_async(self._ai.ask(question, thread_id=msg.chat_id))
            logger.info("AI replied", extra={"reply_len": len(reply) if reply else 0})
            self._send_reply(msg.chat_id, reply or AI_NO_RESPONSE)
        except Exception:
            logger.exception("AI invocation failed")
            self._send_reply(msg.chat_id, "[Erro ao consultar a IA]")

    def _send_reply(self, chat_id: str, text: str) -> None:
        """Send a reply and log it."""
        try:
            self._gateway.send(OutgoingMessage(text=text, chat_id=chat_id))
            logger.info("➡ Sent", extra={"chat_id": chat_id, "text": text[:80]})
        except Exception:
            logger.exception("Failed to send reply")

    @staticmethod
    def _extract_ai_question(text: str) -> str | None:
        """Extract the question from a ``/ia <question>`` message.

        Returns:
            str: The extracted question (empty string if ``/ia`` with no question).
            None: If the message does not start with ``/ia``.
        """
        stripped = text.strip()
        if not stripped.lower().startswith(IA_PREFIX):
            return None
        return stripped[len(IA_PREFIX) :].strip()
