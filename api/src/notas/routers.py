from typing import List

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from core.schemas import ErrorSchema, ResponseSchema
from notas.models import Nota
from notas.schemas import NotaIn, NotaOut, NotaUpdate

router = Router(tags=["notas"])


@router.post("/", response={201: ResponseSchema[NotaOut], 400: ErrorSchema})
def criar_nota(request: HttpRequest, payload: NotaIn) -> tuple[int, ResponseSchema[NotaOut]]:
    """Create a new note."""
    nota = Nota.objects.create(user=request.user, **payload.model_dump())
    return 201, ResponseSchema[NotaOut](data=NotaOut.model_validate(nota))


@router.get("/", response=List[NotaOut])
def listar_notas(request: HttpRequest) -> list[NotaOut]:
    """List all user notes."""
    notas = Nota.objects.filter(user=request.user, arquivada=False)
    return [NotaOut.model_validate(n) for n in notas]


@router.get("/{nota_id}", response={200: NotaOut, 404: ErrorSchema})
def obter_nota(request: HttpRequest, nota_id: int) -> NotaOut:
    """Get a specific note."""
    nota = get_object_or_404(Nota, id=nota_id, user=request.user)
    return NotaOut.model_validate(nota)


@router.put("/{nota_id}", response={200: NotaOut, 404: ErrorSchema})
def atualizar_nota(request: HttpRequest, nota_id: int, payload: NotaUpdate) -> NotaOut:
    """Update a note."""
    nota = get_object_or_404(Nota, id=nota_id, user=request.user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(nota, key, value)
    nota.save()
    return NotaOut.model_validate(nota)


@router.delete("/{nota_id}", response={204: None, 404: ErrorSchema})
def deletar_nota(request: HttpRequest, nota_id: int) -> tuple[int, None]:
    """Delete a note."""
    nota = get_object_or_404(Nota, id=nota_id, user=request.user)
    nota.delete()
    return 204, None
