from typing import List

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from core.schemas import ErrorSchema, ResponseSchema
from lembretes.models import Lembrete
from lembretes.schemas import LembreteIn, LembreteOut, LembreteUpdate

router = Router(tags=["lembretes"])


@router.post("/", response={201: ResponseSchema[LembreteOut], 400: ErrorSchema})
def criar_lembrete(
    request: HttpRequest, payload: LembreteIn
) -> tuple[int, ResponseSchema[LembreteOut]]:
    """Create a new reminder."""
    lembrete = Lembrete.objects.create(user=request.user, **payload.model_dump())
    return 201, ResponseSchema[LembreteOut](data=LembreteOut.model_validate(lembrete))


@router.get("/", response=List[LembreteOut])
def listar_lembretes(request: HttpRequest) -> list[LembreteOut]:
    """List all user reminders."""
    lembretes = Lembrete.objects.filter(user=request.user, concluido=False)
    return [LembreteOut.model_validate(lembrete) for lembrete in lembretes]


@router.get("/{lembrete_id}", response={200: LembreteOut, 404: ErrorSchema})
def obter_lembrete(request: HttpRequest, lembrete_id: int) -> LembreteOut:
    """Get a specific reminder."""
    lembrete = get_object_or_404(Lembrete, id=lembrete_id, user=request.user)
    return LembreteOut.model_validate(lembrete)


@router.put("/{lembrete_id}", response={200: LembreteOut, 404: ErrorSchema})
def atualizar_lembrete(
    request: HttpRequest, lembrete_id: int, payload: LembreteUpdate
) -> LembreteOut:
    """Update a reminder."""
    lembrete = get_object_or_404(Lembrete, id=lembrete_id, user=request.user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(lembrete, key, value)
    lembrete.save()
    return LembreteOut.model_validate(lembrete)


@router.delete("/{lembrete_id}", response={204: None, 404: ErrorSchema})
def deletar_lembrete(request: HttpRequest, lembrete_id: int) -> tuple[int, None]:
    """Delete a reminder."""
    lembrete = get_object_or_404(Lembrete, id=lembrete_id, user=request.user)
    lembrete.delete()
    return 204, None
