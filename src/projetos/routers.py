from typing import List

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from core.schemas import ErrorSchema, ResponseSchema
from projetos.models import Projeto, TarefaProjeto
from projetos.schemas import (
    ProjetoIn,
    ProjetoOut,
    ProjetoUpdate,
    TarefaProjetoIn,
    TarefaProjetoOut,
    TarefaProjetoUpdate,
)

router = Router(tags=["projetos"])


@router.post("/", response={201: ResponseSchema[ProjetoOut], 400: ErrorSchema})
def criar_projeto(
    request: HttpRequest, payload: ProjetoIn
) -> tuple[int, ResponseSchema[ProjetoOut]]:
    """Create a new project."""
    projeto = Projeto.objects.create(user=request.user, **payload.model_dump())
    return 201, ResponseSchema[ProjetoOut](
        data=ProjetoOut.model_validate(projeto), message="Projeto criado com sucesso"
    )


@router.get("/", response=list[ProjetoOut])
def listar_projetos(request: HttpRequest) -> list[ProjetoOut]:
    """List all user projects."""
    projetos = Projeto.objects.filter(user=request.user)
    return [ProjetoOut.model_validate(p) for p in projetos]


@router.get("/{projeto_id}", response={200: ProjetoOut, 404: ErrorSchema})
def obter_projeto(request: HttpRequest, projeto_id: int) -> ProjetoOut:
    """Get a specific project."""
    projeto = get_object_or_404(Projeto, id=projeto_id, user=request.user)
    return ProjetoOut.model_validate(projeto)


@router.put("/{projeto_id}", response={200: ProjetoOut, 404: ErrorSchema})
def atualizar_projeto(request: HttpRequest, projeto_id: int, payload: ProjetoUpdate) -> ProjetoOut:
    """Update a project."""
    projeto = get_object_or_404(Projeto, id=projeto_id, user=request.user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(projeto, key, value)
    projeto.save()
    return ProjetoOut.model_validate(projeto)


@router.delete("/{projeto_id}", response={204: None, 404: ErrorSchema})
def deletar_projeto(request: HttpRequest, projeto_id: int) -> tuple[int, None]:
    """Delete a project."""
    projeto = get_object_or_404(Projeto, id=projeto_id, user=request.user)
    projeto.delete()
    return 204, None


@router.post(
    "/tarefas/",
    response={201: ResponseSchema[TarefaProjetoOut], 400: ErrorSchema},
)
def criar_tarefa_projeto(
    request: HttpRequest, payload: TarefaProjetoIn
) -> tuple[int, ResponseSchema[TarefaProjetoOut]]:
    """Create a new project task."""
    projeto = get_object_or_404(Projeto, id=payload.projeto_id, user=request.user)
    tarefa = TarefaProjeto.objects.create(
        user=request.user,
        projeto=projeto,
        titulo=payload.titulo,
        descricao=payload.descricao,
        ordem=payload.ordem,
    )
    return 201, ResponseSchema[TarefaProjetoOut](data=TarefaProjetoOut.model_validate(tarefa))


@router.get("/tarefas/", response=List[TarefaProjetoOut])
def listar_tarefas_projeto(
    request: HttpRequest, projeto_id: int | None = None
) -> list[TarefaProjetoOut]:
    """List project tasks."""
    queryset = TarefaProjeto.objects.filter(user=request.user)
    if projeto_id:
        queryset = queryset.filter(projeto_id=projeto_id)
    return [TarefaProjetoOut.model_validate(t) for t in queryset]


@router.put(
    "/tarefas/{tarefa_id}",
    response={200: TarefaProjetoOut, 404: ErrorSchema},
)
def atualizar_tarefa_projeto(
    request: HttpRequest, tarefa_id: int, payload: TarefaProjetoUpdate
) -> TarefaProjetoOut:
    """Update a project task."""
    tarefa = get_object_or_404(TarefaProjeto, id=tarefa_id, user=request.user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(tarefa, key, value)
    tarefa.save()
    return TarefaProjetoOut.model_validate(tarefa)


@router.delete("/tarefas/{tarefa_id}", response={204: None, 404: ErrorSchema})
def deletar_tarefa_projeto(request: HttpRequest, tarefa_id: int) -> tuple[int, None]:
    """Delete a project task."""
    tarefa = get_object_or_404(TarefaProjeto, id=tarefa_id, user=request.user)
    tarefa.delete()
    return 204, None
