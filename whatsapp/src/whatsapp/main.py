"""Composition root — wires all adapters and starts the bot.

This is the ONLY place where concrete infrastructure adapters are
imported and connected to abstract domain ports. No framework DI needed.
"""

from __future__ import annotations

import asyncio
import logging
import sys

from jayce import bootstrap, create_agent_service

from .infrastructure.logging import setup_logging

import threading

logger = logging.getLogger(__name__)


def _run_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Thread target to keep the event loop running."""
    asyncio.set_event_loop(loop)
    loop.run_forever()


def run(*, show_qr: bool = True) -> None:
    """Bootstrap jayce, build graph, wire adapters, start bot.

    This function blocks until the neonize connection ends.
    """
    # 0. Logging — must be first
    setup_logging(level="DEBUG")
    logger.info("=" * 60)
    logger.info("WhatsApp Bot starting")
    logger.info("=" * 60)

    from .infrastructure.config import AllowListContactPolicy, WhatsAppSettings
    from .infrastructure.jayce_adapter import JayceAIAdapter
    from .infrastructure.neonize_adapter import NeonizeAdapter

    # 1. Prepare persistent Event Loop for Jayce/LangGraph
    # This loop runs in a background thread to stay alive while neonize blocks main thread.
    loop = asyncio.new_event_loop()
    loop_thread = threading.Thread(target=_run_loop, args=(loop,), daemon=True)
    loop_thread.start()

    # 2. Config
    settings = WhatsAppSettings()
    store_path = settings.store_path_resolved().as_posix()
    logger.info("Config loaded", extra={
        "store_path": store_path,
        "allowed_senders": settings.allowed_senders,
        "allowed_jids": settings.allowed_jids,
    })

    # 3. Jayce (AI engine) — bootstrap and build graph INSIDE the background loop
    async def _setup_ai():
        logger.info("Bootstrapping jayce AI engine (in background loop)...")
        # Bootstrap and create agent inside the loop to ensure thread affinity
        jayce_settings = bootstrap()
        agent = create_agent_service(jayce_settings)

        logger.info("Building compiled graph...")
        # Get the context manager
        ctx = await agent.build_compiled_graph()
        # Enter the context manager and keep it open
        graph = await ctx.__aenter__()
        return agent, graph

    # Run the setup in the background loop and wait for result
    future = asyncio.run_coroutine_threadsafe(_setup_ai(), loop)
    agent, graph = future.result(timeout=60)
    
    logger.info("Jayce and Graph ready in background loop")

    # 4. Wire adapters → ports
    ai = JayceAIAdapter(agent=agent, graph=graph)
    gateway = NeonizeAdapter(store_path=store_path, show_qr=show_qr)
    contact_policy = AllowListContactPolicy(
        allowed_names=settings.allowed_senders,
        allowed_jids=settings.allowed_jids,
    )
    logger.info("All adapters wired")

    # 5. Create service and start (blocks on neonize connect in main thread)
    from .application.bot_service import BotService

    bot = BotService(
        gateway=gateway, 
        ai=ai, 
        contact_policy=contact_policy,
        loop=loop
    )
    logger.info("Starting BotService (blocking on neonize connect)...")
    bot.start()


def cli() -> None:
    """CLI entry point (project.scripts)."""
    run()
