from typing import List

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from core.schemas import ErrorSchema, ResponseSchema
from financas.models import Transacao
from financas.schemas import TransacaoIn, TransacaoOut, TransacaoUpdate

router = Router(tags=["financas"])


@router.post("/", response={201: ResponseSchema[TransacaoOut], 400: ErrorSchema})
def criar_transacao(
    request: HttpRequest, payload: TransacaoIn
) -> tuple[int, ResponseSchema[TransacaoOut]]:
    """Create a new transaction."""
    transacao = Transacao.objects.create(user=request.user, **payload.model_dump())
    return 201, ResponseSchema(data=TransacaoOut.model_validate(transacao))


@router.get("/", response=List[TransacaoOut])
def listar_transacoes(request: HttpRequest) -> list[TransacaoOut]:
    """List all user transactions."""
    transacoes = Transacao.objects.filter(user=request.user)
    return [TransacaoOut.model_validate(t) for t in transacoes]


@router.get("/{transacao_id}", response={200: TransacaoOut, 404: ErrorSchema})
def obter_transacao(request: HttpRequest, transacao_id: int) -> TransacaoOut:
    """Get a specific transaction."""
    transacao = get_object_or_404(Transacao, id=transacao_id, user=request.user)
    return TransacaoOut.model_validate(transacao)


@router.put("/{transacao_id}", response={200: TransacaoOut, 404: ErrorSchema})
def atualizar_transacao(
    request: HttpRequest, transacao_id: int, payload: TransacaoUpdate
) -> TransacaoOut:
    """Update a transaction."""
    transacao = get_object_or_404(Transacao, id=transacao_id, user=request.user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(transacao, key, value)
    transacao.save()
    return TransacaoOut.model_validate(transacao)


@router.delete("/{transacao_id}", response={204: None, 404: ErrorSchema})
def deletar_transacao(request: HttpRequest, transacao_id: int) -> tuple[int, None]:
    """Delete a transaction."""
    transacao = get_object_or_404(Transacao, id=transacao_id, user=request.user)
    transacao.delete()
    return 204, None
