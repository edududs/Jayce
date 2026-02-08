# 🌐 API - Django Application

Backend REST API para o Assistente de Produtividade, construído com Django 6.0 e django-ninja.

## ✨ Features

- **Django Ninja** - API REST moderna e tipada
- **Modular Apps** - Separação de domínios (tarefas, calendário, finanças, etc.)
- **AI Integration** - Consome `jayce` como biblioteca externa

## 📦 Apps Django

| App          | Descrição                       |
| ------------ | ------------------------------- |
| `core`       | Configurações e URLs principais |
| `tarefas`    | Gerenciamento de tarefas        |
| `calendario` | Eventos e agenda                |
| `financas`   | Controle financeiro             |
| `notas`      | Anotações e documentos          |
| `lembretes`  | Sistema de lembretes            |
| `habitos`    | Tracker de hábitos              |
| `projetos`   | Gestão de projetos              |
| `analises`   | Analytics e relatórios          |

## 🚀 Quick Start

```bash
# No diretório raiz do workspace
cd api

# Rodar migrations
uv run python manage.py migrate

# Criar superuser
uv run python manage.py createsuperuser

# Rodar servidor de desenvolvimento
uv run python manage.py runserver
```

## 🔌 Usando Jayce no Django

```python
# Em qualquer view ou service do Django

from jayce import create_assistant, JayceConfig

# Criar assistant com configuração personalizada
config = JayceConfig(
    model_name="ollama:llama3.1",
    system_prompt="Você é um assistente de produtividade..."
)
assistant = create_assistant(config)

# Usar em uma view
def chat_view(request):
    user_message = request.data.get("message")
    response = assistant.chat(user_message)
    return {"response": response}
```

## 📁 Estrutura

```
api/
├── manage.py           # Django management
├── pyproject.toml      # Package config
├── src/
│   ├── core/           # Settings, URLs, WSGI
│   ├── tarefas/        # Tasks app
│   ├── calendario/     # Calendar app
│   ├── financas/       # Finance app
│   ├── notas/          # Notes app
│   ├── lembretes/      # Reminders app
│   ├── habitos/        # Habits app
│   ├── projetos/       # Projects app
│   └── analises/       # Analytics app
└── tests/
```

## 🧪 Testing

```bash
uv run pytest api/tests
```
