"""NeonizeAdapter — MessageGateway implementation using neonize.

Encapsulates 100% of neonize-specific logic: client creation, event
registration, protobuf→domain translation, message sending.

No other layer imports neonize directly.
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from ..domain.models import IncomingMessage, OutgoingMessage
from ..domain.ports import MessageGateway

if TYPE_CHECKING:
    from neonize.client import NewClient

logger = logging.getLogger(__name__)


class NeonizeAdapter(MessageGateway):
    """Neonize-specific implementation of MessageGateway.

    Wraps neonize's event-driven/callback API into the port abstraction.
    """

    def __init__(self, store_path: str, *, show_qr: bool = True) -> None:
        self._store_path = store_path
        self._show_qr = show_qr
        self._client: NewClient | None = None
        self._callback: Callable[[IncomingMessage], None] | None = None
        logger.debug("NeonizeAdapter created", extra={"store_path": store_path, "show_qr": show_qr})

    def on_message(self, callback: Callable[[IncomingMessage], None]) -> None:
        """Register the callback BEFORE connect()."""
        self._callback = callback
        logger.debug("on_message callback registered", extra={"callback": callback.__qualname__})

    def send(self, message: OutgoingMessage) -> None:
        """Send a message through WhatsApp."""
        if self._client is None:
            msg = "Not connected — call connect() first"
            raise RuntimeError(msg)
        from neonize.utils.jid import build_jid

        jid = build_jid(message.chat_id)
        logger.info("Sending message", extra={"chat_id": message.chat_id, "text_len": len(message.text)})
        self._client.send_message(jid, message.text)
        logger.debug("Message sent OK", extra={"chat_id": message.chat_id})

    def connect(self) -> None:
        """Create the neonize client, register events, and connect (blocks)."""
        from neonize.client import NewClient
        from neonize.proto.Neonize_pb2 import Message as MessageEv

        logger.info("Creating neonize client", extra={"store_path": self._store_path})
        self._client = NewClient(self._store_path)

        if self._show_qr:
            self._client.qr(self._handle_qr)
            logger.debug("QR handler registered")

        # Bridge neonize's event decorator → our domain callback.
        # Use a plain closure wrapper because neonize's CGo bridge
        # may not correctly invoke bound methods.
        handler = self._on_neonize_message

        @self._client.event(MessageEv)
        def on_message(client: NewClient, message: Any) -> None:  # noqa: ANN401
            handler(client, message)

        logger.info("Event handler registered, connecting...")
        self._client.connect()  # blocks until disconnect
        logger.info("Neonize disconnected")

    def _on_neonize_message(self, client: NewClient, message: Any) -> None:
        """Translate neonize protobuf event → domain IncomingMessage."""
        logger.debug(">>> RAW neonize event received")

        from neonize.utils.jid import Jid2String
        from neonize.utils.message import extract_text

        source = message.Info.MessageSource
        is_from_me = getattr(source, "IsFromMe", False)

        logger.debug("Message source", extra={
            "is_from_me": is_from_me,
            "chat": str(getattr(source, "Chat", "?")),
            "sender": str(getattr(source, "Sender", "?")),
        })

        try:
            text = extract_text(message.Message) or ""
        except (IndexError, AttributeError, TypeError):
            logger.debug("Could not extract text from message (media?)")
            text = ""

        if not text.strip():
            logger.debug("Empty text, skipping")
            return

        chat_jid = source.Chat
        sender_jid = getattr(source, "Sender", chat_jid)

        chat_id = self._jid_to_str(chat_jid)
        sender_id = self._jid_to_str(sender_jid)

        # Resolve sender display name from contacts.
        # Try sender_jid first, then fall back to chat_jid (for DMs
        # where the chat IS the contact). Also try multiple attributes
        # since neonize contact objects vary between versions.
        sender_name = ""
        for jid_to_try in (sender_jid, chat_jid):
            if sender_name:
                break
            try:
                contact = client.contact.get_contact(jid_to_try)
                logger.debug("Contact lookup result", extra={
                    "jid": self._jid_to_str(jid_to_try),
                    "contact_type": type(contact).__name__,
                    "attrs": {k: getattr(contact, k, None) for k in dir(contact) if not k.startswith("_")},
                })
                # Try multiple name fields
                for attr in ("FullName", "PushName", "BusinessName", "FirstName"):
                    name = getattr(contact, attr, None)
                    if name and str(name).strip():
                        sender_name = str(name).strip()
                        logger.debug("Resolved name", extra={"attr": attr, "name": sender_name})
                        break
            except Exception:  # noqa: BLE001
                logger.debug("get_contact failed", extra={"jid": self._jid_to_str(jid_to_try)})

        # Fallback: try PushName from message info itself
        if not sender_name:
            push = getattr(message.Info, "PushName", None)
            if push and str(push).strip():
                sender_name = str(push).strip()
                logger.debug("Using PushName from message info", extra={"push_name": sender_name})

        logger.info("Message received", extra={
            "chat_id": chat_id,
            "sender_id": sender_id,
            "sender_name": sender_name,
            "is_from_me": is_from_me,
            "text": text[:80],
        })

        incoming = IncomingMessage(
            text=text,
            chat_id=chat_id,
            sender_id=sender_id,
            sender_name=sender_name,
            is_from_me=is_from_me,
        )

        if self._callback is not None:
            logger.debug("Dispatching to callback")
            self._callback(incoming)
        else:
            logger.warning("No callback registered — message dropped!")

    @staticmethod
    def _jid_to_str(jid: Any) -> str:
        """Normalize a neonize JID to a plain string."""
        if jid is None:
            return ""
        from neonize.utils.jid import Jid2String

        return Jid2String(jid) if hasattr(jid, "User") else str(jid)

    @staticmethod
    def _handle_qr(_client: object, data_qr: bytes) -> None:
        """Render the QR code in the terminal for first-time login."""
        print(
            "\n--- Escaneie o QR code com o WhatsApp (Aparelhos conectados) ---\n",
            file=sys.stderr,
        )
        import segno

        segno.make_qr(data_qr).terminal(compact=True)
