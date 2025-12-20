# Assistente

Assistente pessoal inteligente voltado para produtividade e organização individual, atuando como um centro de gestão "tudo-em-um" (all-in-one). Plataforma API-first desenhada para otimizar a rotina diária através de uma arquitetura modular e integrada.

## Diferenciais

- **API-First**: Arquitetura RESTful completa, sem dependência de templates ou interfaces web
- **Modularidade**: Sistema composto por apps Django independentes com alta coesão e baixo acoplamento
- **Flexibilidade**: Estrutura extensível que permite adicionar novas funcionalidades sem impacto nas existentes
- **Padrões Modernos**: Uso de Pydantic para validação, django-ninja para API e TextChoices do Django

## Funcionalidades

O sistema oferece um ecossistema completo para gestão pessoal através de módulos especializados:

### 📋 Tarefas
Gerenciamento de tarefas com prioridades, prazos e status de conclusão.

### 📅 Calendário
Eventos e compromissos com suporte a recorrência e frequências personalizadas.

### 💰 Finanças
Controle financeiro pessoal com categorização de receitas e despesas.

### 📝 Notas
Organização de pensamentos e anotações com sistema de tags.

### 🔔 Lembretes
Sistema de lembretes com prioridades e notificações agendadas.

### 🎯 Hábitos
Rastreamento de hábitos com frequência desejada e histórico de registros.

### 📊 Projetos
Gestão de projetos com status, prazos e tarefas associadas.

### 📈 Análises
Métricas e análises personalizadas para visualizar progresso e tendências.

## Tecnologias

- **Django 6.0+**: Framework web Python
- **django-ninja**: Framework moderno para construção de APIs REST
- **Pydantic 2.12+**: Validação de dados e serialização
- **Python 3.13+**: Linguagem de programação

## Arquitetura

O projeto segue princípios de design priorizados:

1. **Zen of Python**: Legibilidade e simplicidade
2. **DRY**: Evita repetição de código
3. **KISS**: Mantém soluções simples
4. **SOLID**: Alta coesão e baixo acoplamento

### Estrutura do Projeto

```
src/
├── core/              # Configurações centrais e base compartilhada
│   ├── models.py      # Models base (TimestampedModel, UserOwnedModel)
│   ├── schemas.py     # Schemas Pydantic base
│   └── api.py         # Configuração da API principal
├── tarefas/           # App de gerenciamento de tarefas
├── calendario/        # App de eventos e calendário
├── financas/          # App de controle financeiro
├── notas/             # App de notas e anotações
├── lembretes/         # App de lembretes
├── habitos/           # App de rastreamento de hábitos
├── projetos/          # App de gestão de projetos
└── analises/          # App de métricas e análises
```

Cada app contém:
- `models.py`: Modelos Django com classes de choices
- `schemas.py`: Schemas Pydantic para validação
- `routers.py`: Endpoints da API usando django-ninja

## Instalação

### Pré-requisitos

- Python 3.13+
- uv (gerenciador de pacotes)

### Setup

1. Clone o repositório:
```bash
git clone <repository-url>
cd assistente
```

2. Instale as dependências:
```bash
uv sync
```

3. Execute as migrações:
```bash
uv run python src/manage.py migrate
```

4. Crie um superusuário (opcional):
```bash
uv run python src/manage.py createsuperuser
```

5. Inicie o servidor:
```bash
uv run python src/manage.py runserver
```

## API

A API está disponível em `/api/` e a documentação interativa em `/api/docs`.

### Endpoints Principais

- `GET /api/tarefas/` - Lista todas as tarefas
- `POST /api/tarefas/` - Cria uma nova tarefa
- `GET /api/calendario/` - Lista todos os eventos
- `POST /api/calendario/` - Cria um novo evento
- `GET /api/financas/` - Lista todas as transações
- `POST /api/financas/` - Cria uma nova transação
- `GET /api/notas/` - Lista todas as notas
- `POST /api/notas/` - Cria uma nova nota
- `GET /api/lembretes/` - Lista todos os lembretes
- `POST /api/lembretes/` - Cria um novo lembrete
- `GET /api/habitos/` - Lista todos os hábitos
- `POST /api/habitos/` - Cria um novo hábito
- `GET /api/projetos/` - Lista todos os projetos
- `POST /api/projetos/` - Cria um novo projeto
- `GET /api/analises/` - Lista todas as métricas
- `POST /api/analises/` - Cria uma nova métrica

Cada recurso suporta operações CRUD completas (Create, Read, Update, Delete).

### Autenticação

A API utiliza autenticação do Django (`django_auth`). Todas as requisições requerem autenticação de usuário.

## Desenvolvimento

### Executar testes

```bash
uv run python src/manage.py test
```

### Criar migrações

```bash
uv run python src/manage.py makemigrations
```

### Aplicar migrações

```bash
uv run python src/manage.py migrate
```
