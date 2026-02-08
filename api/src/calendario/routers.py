from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from calendario.models import Evento
from calendario.schemas import EventoIn, EventoOut, EventoUpdate
from core.schemas import ErrorSchema, ResponseSchema

router = Router(tags=["calendario"])


@router.post("/", response={201: ResponseSchema[EventoOut], 400: ErrorSchema})
def criar_evento(request: HttpRequest, payload: EventoIn) -> tuple[int, ResponseSchema[EventoOut]]:
    """Create a new event."""
    evento = Evento.objects.create(user=request.user, **payload.model_dump())
    return 201, ResponseSchema[EventoOut](data=EventoOut.model_validate(evento))


@router.get("/", response=list[EventoOut])
def listar_eventos(request: HttpRequest) -> list[EventoOut]:
    """List all user events."""
    eventos = Evento.objects.filter(user=request.user)
    return [EventoOut.model_validate(e) for e in eventos]


@router.get("/{evento_id}", response={200: EventoOut, 404: ErrorSchema})
def obter_evento(request: HttpRequest, evento_id: int) -> EventoOut:
    """Get a specific event."""
    evento = get_object_or_404(Evento, id=evento_id, user=request.user)
    return EventoOut.model_validate(evento)


@router.put("/{evento_id}", response={200: EventoOut, 404: ErrorSchema})
def atualizar_evento(request: HttpRequest, evento_id: int, payload: EventoUpdate) -> EventoOut:
    """Update an event."""
    evento = get_object_or_404(Evento, id=evento_id, user=request.user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(evento, key, value)
    evento.save()
    return EventoOut.model_validate(evento)


@router.delete("/{evento_id}", response={204: None, 404: ErrorSchema})
def deletar_evento(request: HttpRequest, evento_id: int) -> tuple[int, None]:
    """Delete an event."""
    evento = get_object_or_404(Evento, id=evento_id, user=request.user)
    evento.delete()
    return 204, None
