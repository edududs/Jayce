from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from analises.models import Metrica, RegistroMetrica
from analises.schemas import (
    MetricaIn,
    MetricaOut,
    MetricaUpdate,
    RegistroMetricaIn,
    RegistroMetricaOut,
)
from core.schemas import ErrorSchema, ResponseSchema

router = Router(tags=["analises"])


@router.post("/", response={201: ResponseSchema[MetricaOut], 400: ErrorSchema})
def criar_metrica(
    request: HttpRequest, payload: MetricaIn
) -> tuple[int, ResponseSchema[MetricaOut]]:
    """Create a new metric."""
    metrica = Metrica.objects.create(user=request.user, **payload.model_dump())
    return 201, ResponseSchema[MetricaOut](data=MetricaOut.model_validate(metrica))


@router.get("/", response=list[MetricaOut])
def listar_metricas(request: HttpRequest) -> list[MetricaOut]:
    """List all user metrics."""
    metricas = Metrica.objects.filter(user=request.user, ativa=True)
    return [MetricaOut.model_validate(m) for m in metricas]


@router.get("/{metrica_id}", response={200: MetricaOut, 404: ErrorSchema})
def obter_metrica(request: HttpRequest, metrica_id: int) -> MetricaOut:
    """Get a specific metric."""
    metrica = get_object_or_404(Metrica, id=metrica_id, user=request.user)
    return MetricaOut.model_validate(metrica)


@router.put("/{metrica_id}", response={200: MetricaOut, 404: ErrorSchema})
def atualizar_metrica(request: HttpRequest, metrica_id: int, payload: MetricaUpdate) -> MetricaOut:
    """Update a metric."""
    metrica = get_object_or_404(Metrica, id=metrica_id, user=request.user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(metrica, key, value)
    metrica.save()
    return MetricaOut.model_validate(metrica)


@router.delete("/{metrica_id}", response={204: None, 404: ErrorSchema})
def deletar_metrica(request: HttpRequest, metrica_id: int) -> tuple[int, None]:
    """Delete a metric."""
    metrica = get_object_or_404(Metrica, id=metrica_id, user=request.user)
    metrica.delete()
    return 204, None


@router.post(
    "/registros/",
    response={201: ResponseSchema[RegistroMetricaOut], 400: ErrorSchema},
)
def criar_registro(
    request: HttpRequest, payload: RegistroMetricaIn
) -> tuple[int, ResponseSchema[RegistroMetricaOut]]:
    """Create a new metric record."""
    metrica = get_object_or_404(Metrica, id=payload.metrica_id, user=request.user)
    registro = RegistroMetrica.objects.create(
        user=request.user,
        metrica=metrica,
        valor=payload.valor,
        data=payload.data,
        observacoes=payload.observacoes,
    )
    return 201, ResponseSchema[RegistroMetricaOut](data=RegistroMetricaOut.model_validate(registro))


@router.get("/registros/", response=list[RegistroMetricaOut])
def listar_registros(
    request: HttpRequest, metrica_id: int | None = None
) -> list[RegistroMetricaOut]:
    """List metric records."""
    queryset = RegistroMetrica.objects.filter(user=request.user)
    if metrica_id:
        queryset = queryset.filter(metrica_id=metrica_id)
    return [RegistroMetricaOut.model_validate(r) for r in queryset]
