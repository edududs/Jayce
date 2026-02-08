# 🤖 Jayce - AI Engine

**Jayce** is a pure Python library for AI orchestration using LangGraph. It provides a clean, framework-agnostic interface for building conversational AI agents.

## ✨ Features

- **Zero Django Dependencies** - Pure Python, use it anywhere
- **LangGraph Powered** - Built on the latest LangGraph for reliable agent workflows
- **Multiple LLM Providers** - Support for Ollama, OpenAI, Anthropic, Google
- **Sensible Defaults** - Works out of the box with KISS principles
- **Dependency Injection** - Fully configurable and testable
- **Async Support** - Both sync and async APIs

## 📦 Installation

```bash
# As part of the workspace
uv sync

# With optional providers
uv add jayce[openai]      # For OpenAI support
uv add jayce[anthropic]   # For Anthropic support
uv add jayce[all]         # All providers
```

## 🚀 Quick Start

```python
from jayce import create_assistant, JayceConfig

# With defaults (uses Ollama llama3.1)
assistant = create_assistant()
response = assistant.chat("What is LangGraph?")
print(response)

# With custom configuration
config = JayceConfig(
    model_name="openai:gpt-4o",
    temperature=0.7,
    system_prompt="You are a helpful coding assistant.",
)
assistant = create_assistant(config)
response = assistant.chat("How do I use async/await in Python?")
```

## ⚙️ Configuration

```python
from jayce import JayceConfig

config = JayceConfig(
    # LLM Settings
    model_name="ollama:llama3.1",  # Format: "provider:model"
    temperature=0.7,
    max_tokens=None,  # None = model default

    # System Prompt
    system_prompt="You are a helpful assistant...",

    # Tool Settings
    tools=ToolConfig(
        enable_search=True,
        tavily_api_key="...",  # Or set TAVILY_API_KEY env var
        tavily_max_results=5,
    ),

    # Memory
    enable_memory=True,
    thread_id="custom-thread-123",
)
```

## 🏗️ Architecture

```
jayce/
├── src/jayce/
│   ├── __init__.py     # Public exports
│   ├── factory.py      # Main facade (entry point)
│   ├── cli.py          # CLI interface
│   ├── core/           # LangGraph workflows
│   │   └── graph.py    # Graph builder
│   ├── nodes/          # Atomic node functions
│   │   ├── llm.py      # LLM call node
│   │   └── tools.py    # Tool execution node
│   ├── schemas/        # Pydantic V2 models
│   │   ├── config.py   # Configuration schema
│   │   └── state.py    # Agent state schema
│   └── utils/          # Helper functions
│       └── formatters.py
└── tests/
```

## 🧪 Testing

```bash
# Run tests
uv run pytest jayce/tests

# With coverage
uv run pytest jayce/tests --cov=jayce
```

## 📄 License

MIT
