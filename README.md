# 🤖 Assistente - Sistema de Produtividade com IA

Monorepo para um sistema de produtividade pessoal integrado com IA, construído usando **uv Workspaces**.

## 📦 Arquitetura

```
.
├── pyproject.toml          # Root workspace configuration
├── .env                    # Environment variables (TAVILY_API_KEY, etc.)
│
├── api/                    # 📦 Django Application Package
│   ├── pyproject.toml
│   ├── manage.py
│   └── src/
│       ├── core/           # Django settings & API routes
│       ├── tarefas/        # Tasks management
│       ├── calendario/     # Calendar & events
│       ├── financas/       # Finance tracking
│       ├── notas/          # Notes & documents
│       ├── lembretes/      # Reminders
│       ├── habitos/        # Habit tracking
│       ├── projetos/       # Project management
│       └── analises/       # Analytics
│
└── jayce/                  # 📦 AI Engine Package (Pure Python)
    ├── pyproject.toml
    └── src/jayce/
        ├── core/           # LangGraph workflows
        ├── factory.py      # Main facade (entry point)
        ├── nodes/          # Atomic LLM/Tool nodes
        ├── schemas/        # Pydantic V2 models
        └── utils/          # Helper functions
```

## 🏗️ Princípios de Design

| Princípio                | Implementação                                             |
| ------------------------ | --------------------------------------------------------- |
| **SOLID**                | Jayce é Single Responsibility - apenas orquestração de IA |
| **Low Coupling**         | Jayce NÃO importa nada de Django/API                      |
| **Dependency Injection** | Factory pattern com configuração injetada                 |
| **KISS**                 | Defaults sensíveis, funciona "out of the box"             |

## 🚀 Quick Start

```bash
# Clone e entre no diretório
cd assistente

# Sync todas as dependências do workspace
uv sync --all-packages

# Rodar servidor Django
uv run python api/manage.py runserver

# Ou usar o CLI do Jayce diretamente
uv run jayce
```

## 💡 Uso do Jayce (AI Engine)

```python
from jayce import create_assistant, JayceConfig

# Com defaults (Ollama llama3.1)
assistant = create_assistant()
response = assistant.chat("O que é LangGraph?")

# Com configuração customizada
config = JayceConfig(
    model_name="openai:gpt-4o",
    temperature=0.5,
    system_prompt="Você é um assistente de produtividade..."
)
assistant = create_assistant(config)
```

## 🔧 Configuração

Crie um arquivo `.env` na raiz:

```env
# AI/LLM
TAVILY_API_KEY=tvly-xxxxxxxxxxxxx   # Para web search
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx  # Se usar OpenAI

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## 📡 API Endpoints

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/api/docs
- **Chat endpoint**: `POST /api/chat/`
  ```json
  {
    "message": "O que tenho na agenda hoje?",
    "thread_id": "optional-thread-id"
  }
  ```

## 🧪 Testes

```bash
# Rodar todos os testes
uv run pytest

# Apenas Jayce
uv run pytest jayce/tests

# Apenas API
uv run pytest api/tests
```

## 📚 Packages

| Package   | Descrição               | Dependências                   |
| --------- | ----------------------- | ------------------------------ |
| **jayce** | AI Engine com LangGraph | langchain, langgraph, pydantic |
| **api**   | Django REST API         | django, django-ninja, jayce    |

## 🛠️ Desenvolvimento

```bash
# Lint com Ruff
uv run ruff check .
uv run ruff format .

# Type check com Pyright
uv run pyright

# Adicionar dependência ao Jayce
cd jayce && uv add <package>

# Adicionar dependência à API
cd api && uv add <package>
```

---

**Built with ❤️ using uv Workspaces, LangGraph, and Django 6.0**
