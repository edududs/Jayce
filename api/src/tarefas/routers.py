from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from core.schemas import ErrorSchema, ResponseSchema
from tarefas.models import Tarefa
from tarefas.schemas import TarefaIn, TarefaOut, TarefaUpdate

router = Router(tags=["tarefas"])


@router.post("/", response={201: ResponseSchema[TarefaOut], 400: ErrorSchema})
def criar_tarefa(request: HttpRequest, payload: TarefaIn) -> tuple[int, ResponseSchema[TarefaOut]]:
    """Create a new task."""
    tarefa = Tarefa.objects.create(user=request.user, **payload.model_dump())
    return 201, ResponseSchema(data=TarefaOut.model_validate(tarefa))


@router.get("/", response=list[TarefaOut])
def listar_tarefas(request: HttpRequest) -> list[TarefaOut]:
    """List all user tasks."""
    tarefas = Tarefa.objects.filter(user=request.user)
    return [TarefaOut.model_validate(t) for t in tarefas]


@router.get("/{tarefa_id}", response={200: TarefaOut, 404: ErrorSchema})
def obter_tarefa(request: HttpRequest, tarefa_id: int) -> TarefaOut:
    """Get a specific task."""
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, user=request.user)
    return TarefaOut.model_validate(tarefa)


@router.put("/{tarefa_id}", response={200: TarefaOut, 404: ErrorSchema})
def atualizar_tarefa(request: HttpRequest, tarefa_id: int, payload: TarefaUpdate) -> TarefaOut:
    """Update a task."""
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, user=request.user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(tarefa, key, value)
    tarefa.save()
    return TarefaOut.model_validate(tarefa)


@router.delete("/{tarefa_id}", response={204: None, 404: ErrorSchema})
def deletar_tarefa(request: HttpRequest, tarefa_id: int) -> tuple[int, None]:
    """Delete a task."""
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, user=request.user)
    tarefa.delete()
    return 204, None
