"""Configuration and contact policy — infrastructure concerns.

Loads settings from environment/.env and provides contact authorization.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..domain.ports import ContactPolicy


class WhatsAppSettings(BaseSettings):
    """Settings for the WhatsApp bot, loaded from environment.

    Environment variables are prefixed with ``WHATSAPP_``.
    """

    model_config = SettingsConfigDict(
        env_prefix="WHATSAPP_",
        env_file=".env",
        extra="ignore",
    )

    store_path: str = "whatsapp_session.sqlite3"
    """Path to the SQLite store file (neonize session persistence)."""

    allowed_senders: list[str] = Field(
        default_factory=lambda: [
            "amor da minha vida",
            "barbara",
            "joão marcos irmão",
            "joao marcos irmao",
        ],
        description="Contact display names allowed to trigger the bot (case-insensitive).",
    )

    allowed_jids: list[str] = Field(
        default_factory=lambda: [
            "556185341091",     # Barbara (phone number)
            "184129677193251",  # Barbara (LID)
        ],
        description=(
            "Phone numbers or JID prefixes allowed to interact. "
            "Matched as substring against the sender_id or chat_id."
        ),
    )

    def store_path_resolved(self) -> Path:
        """Absolute path for the store file."""
        p = Path(self.store_path)
        return p.resolve() if p.is_absolute() else Path.cwd() / p


class AllowListContactPolicy(ContactPolicy):
    """Contact policy based on display names AND/OR JID prefixes.

    A sender is allowed if:
    - Any ``allowed_names`` entry is a substring of the sender's display name, OR
    - Any ``allowed_jids`` entry is a substring of the sender_id.

    This dual approach handles WhatsApp's LID migration where
    ``sender_name`` may be empty for some contacts.
    """

    def __init__(
        self,
        allowed_names: list[str],
        allowed_jids: list[str] | None = None,
    ) -> None:
        import logging

        self._logger = logging.getLogger(__name__)
        self._allowed_names = frozenset(n.lower() for n in allowed_names)
        self._allowed_jids = frozenset(j.lower() for j in (allowed_jids or []))
        self._logger.debug("AllowListContactPolicy created", extra={
            "allowed_names": list(self._allowed_names),
            "allowed_jids": list(self._allowed_jids),
        })

    def is_allowed(self, sender_name: str, sender_id: str) -> bool:
        """Return True if sender matches by name OR by JID."""
        name = sender_name.strip().lower()
        sid = sender_id.strip().lower()

        # Check by display name
        name_match = bool(name) and any(a in name for a in self._allowed_names)

        # Check by JID/number
        jid_match = bool(sid) and any(j in sid for j in self._allowed_jids)

        result = name_match or jid_match
        self._logger.debug("is_allowed check", extra={
            "sender_name": sender_name or "(empty)",
            "sender_id": sender_id,
            "name_match": name_match,
            "jid_match": jid_match,
            "result": result,
        })
        return result
