"""CLI Adapter — interactive terminal interface using Rich.

This is a driving adapter in the hexagonal architecture: it drives
the application layer (AgentService) via user input.
"""

import asyncio

from rich import print
from rich.markdown import Markdown
from rich.prompt import Prompt

from ..application.agent_service import AgentService
from ..application.bootstrap import bootstrap
from ..infrastructure.checkpointer.adapter import create_checkpoint_adapter
from ..infrastructure.config import JayceSettings
from ..infrastructure.llm.adapter import LangChainLLMAdapter
from ..infrastructure.tools.adapter import LangChainToolRegistryAdapter
from .formatters import format_response_footer


class CLIAdapter:
    """Interactive CLI adapter using Rich for terminal-based agent interaction.

    This adapter wires up all infrastructure dependencies and drives
    the AgentService through a REPL loop.
    """

    def __init__(self, agent: AgentService, *, thread_id: str = "1") -> None:
        self._agent = agent
        self._thread_id = thread_id

    async def run(self) -> None:
        """Start the interactive REPL loop.

        Prefix a message with ``/think`` to engage deep reasoning mode
        (deepseek-r1). Example: ``/think por que o céu é azul?``
        """
        prompt = Prompt()
        Prompt.prompt_suffix = ""

        print("[dim]Dica: prefixe com /think para ativar raciocínio profundo (deepseek-r1)[/dim]")
        print(Markdown("\n\n  ---  \n\n"))

        async with await self._agent.build_compiled_graph() as graph:
            while True:
                user_input = prompt.ask("[bold cyan]Você: \n")
                print(Markdown("\n\n  ---  \n\n"))

                if user_input.lower() in {"q", "quit"}:
                    break

                # Check for /think prefix
                thinking = False
                message = user_input
                if user_input.strip().lower().startswith("/think"):
                    thinking = True
                    message = user_input.strip()[len("/think"):].strip()
                    if not message:
                        print("[yellow]Use: /think <sua pergunta>[/yellow]")
                        continue
                    print("[magenta]🧠 Modo pensamento ativado (deepseek-r1)[/magenta]")

                response = await self._agent.send_message(
                    graph,
                    message,
                    thread_id=self._thread_id,
                    thinking=thinking,
                )

                # Show thinking trace if present
                if response.thinking:
                    print("[dim]━━━ 🧠 Raciocínio ━━━[/dim]")
                    print(f"[dim italic]{response.thinking}[/dim italic]")
                    print("[dim]━━━━━━━━━━━━━━━━━━━━━[/dim]\n")

                print(f"[bold cyan]RESPOSTA ({response.model_name}): \n")
                print(Markdown(response.content))

                footer = format_response_footer(response)
                if footer:
                    print(f"[dim]({footer})[/dim]")

                print(Markdown("\n\n  ---  \n\n"))


def create_agent_service(settings: JayceSettings) -> AgentService:
    """Factory: compose all infrastructure adapters into an AgentService.

    This is the composition root — the only place where concrete
    adapters are wired to abstract ports.
    """
    llm = LangChainLLMAdapter()
    tools = LangChainToolRegistryAdapter(settings)
    checkpoint = create_checkpoint_adapter(settings.db_dsn)

    return AgentService(llm=llm, tools=tools, checkpoint=checkpoint)


async def async_main(settings: JayceSettings) -> None:
    """Async entry point for the CLI."""
    agent = create_agent_service(settings)
    cli = CLIAdapter(agent)
    await cli.run()


def cli() -> None:
    """CLI entry point — bootstrap + run."""
    settings = bootstrap()
    asyncio.run(async_main(settings))
