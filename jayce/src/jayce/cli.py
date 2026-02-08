"""
CLI entry point for Jayce.

Provides a simple command-line interface for interactive chat.
"""

from __future__ import annotations

import re
import sys


def main() -> None:
    """Main entry point for the Jayce CLI."""
    try:
        from rich import print as rprint
        from rich.markdown import Markdown
    except ImportError:
        print("Rich not installed. Run: pip install rich")
        sys.exit(1)

    from jayce import JayceConfig, create_assistant

    rprint(Markdown("# 🤖 Jayce AI Assistant"))
    rprint(Markdown("---"))
    rprint("Type your message and press Enter. Type `exit` or `quit` to leave.\n")

    # Create assistant with defaults
    config = JayceConfig()
    assistant = create_assistant(config)

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            rprint("\n\nBye! 👋")
            break

        if not user_input:
            continue

        if re.fullmatch(r"(exit|quit|sair|q)", user_input, re.IGNORECASE):
            rprint("Bye! 👋")
            break

        rprint(Markdown("---"))

        try:
            response = assistant.chat(user_input)
            rprint(Markdown(response or "_No response._"))
        except Exception as e:  # noqa: BLE001
            rprint(f"[red]Error: {e}[/red]")

        rprint(Markdown("---"))


if __name__ == "__main__":
    main()
