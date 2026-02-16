"""WhatsApp Bot — Hexagonal Architecture.

Public API
----------
- ``WhatsAppSettings``: Configuration loaded from env
- ``BotService``: Application orchestrator
- ``run``, ``cli``: Entry points

Hexagonal layers:
    domain/          — Models, ports (ABCs)
    application/     — Use cases (BotService)
    infrastructure/  — Adapters (Neonize, Jayce, config)
    main.py          — Composition root
"""

from .infrastructure.config import WhatsAppSettings
from .main import cli, run

__all__ = ["WhatsAppSettings", "cli", "run"]
