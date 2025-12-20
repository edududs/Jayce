from typing import List

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from core.schemas import ErrorSchema, ResponseSchema
from habitos.models import Habito, RegistroHabito
from habitos.schemas import (
    HabitoIn,
    HabitoOut,
    HabitoUpdate,
    RegistroHabitoIn,
    RegistroHabitoOut,
)

router = Router(tags=["habitos"])


@router.post("/", response={201: ResponseSchema[HabitoOut], 400: ErrorSchema})
def criar_habito(request: HttpRequest, payload: HabitoIn) -> tuple[int, ResponseSchema[HabitoOut]]:
    """Create a new habit."""
    habito = Habito.objects.create(user=request.user, **payload.model_dump())
    return 201, ResponseSchema[HabitoOut](data=HabitoOut.model_validate(habito))


@router.get("/", response=List[HabitoOut])
def listar_habitos(request: HttpRequest) -> list[HabitoOut]:
    """List all user habits."""
    habitos = Habito.objects.filter(user=request.user, ativo=True)
    return [HabitoOut.model_validate(h) for h in habitos]


@router.get("/{habito_id}", response={200: HabitoOut, 404: ErrorSchema})
def obter_habito(request: HttpRequest, habito_id: int) -> HabitoOut:
    """Get a specific habit."""
    habito = get_object_or_404(Habito, id=habito_id, user=request.user)
    return HabitoOut.model_validate(habito)


@router.put("/{habito_id}", response={200: HabitoOut, 404: ErrorSchema})
def atualizar_habito(request: HttpRequest, habito_id: int, payload: HabitoUpdate) -> HabitoOut:
    """Update a habit."""
    habito = get_object_or_404(Habito, id=habito_id, user=request.user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(habito, key, value)
    habito.save()
    return HabitoOut.model_validate(habito)


@router.delete("/{habito_id}", response={204: None, 404: ErrorSchema})
def deletar_habito(request: HttpRequest, habito_id: int) -> tuple[int, None]:
    """Delete a habit."""
    habito = get_object_or_404(Habito, id=habito_id, user=request.user)
    habito.delete()
    return 204, None


@router.post(
    "/registros/",
    response={201: ResponseSchema[RegistroHabitoOut], 400: ErrorSchema},
)
def criar_registro(
    request: HttpRequest, payload: RegistroHabitoIn
) -> tuple[int, ResponseSchema[RegistroHabitoOut]]:
    """Create a new habit record."""
    habito = get_object_or_404(Habito, id=payload.habito_id, user=request.user)
    registro = RegistroHabito.objects.create(
        user=request.user,
        habito=habito,
        data=payload.data,
        observacoes=payload.observacoes,
    )
    registro_data = RegistroHabitoOut.model_validate(registro)
    return 201, ResponseSchema[RegistroHabitoOut](data=registro_data)


@router.get("/registros/", response=List[RegistroHabitoOut])
def listar_registros(request: HttpRequest, habito_id: int | None = None) -> list[RegistroHabitoOut]:
    """List habit records."""
    queryset = RegistroHabito.objects.filter(user=request.user)
    if habito_id:
        queryset = queryset.filter(habito_id=habito_id)
    return [RegistroHabitoOut.model_validate(r) for r in queryset]
