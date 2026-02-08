from ninja import NinjaAPI
from ninja.security import django_auth

from analises.routers import router as analises_router
from calendario.routers import router as calendario_router
from core.chat_router import router as chat_router
from financas.routers import router as financas_router
from habitos.routers import router as habitos_router
from lembretes.routers import router as lembretes_router
from notas.routers import router as notas_router
from projetos.routers import router as projetos_router
from tarefas.routers import router as tarefas_router

api = NinjaAPI(
    title="Assistente API",
    version="1.0.0",
    description="Sistema integrado de produtividade com IA",
    auth=django_auth,
)

# Domain routers (require auth)
api.add_router("/tarefas", tarefas_router)
api.add_router("/calendario", calendario_router)
api.add_router("/financas", financas_router)
api.add_router("/notas", notas_router)
api.add_router("/lembretes", lembretes_router)
api.add_router("/habitos", habitos_router)
api.add_router("/projetos", projetos_router)
api.add_router("/analises", analises_router)

# AI Chat router (Jayce integration - no auth for demo)
api.add_router("/chat", chat_router, auth=None)
