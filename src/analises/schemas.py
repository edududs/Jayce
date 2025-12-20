from datetime import date
from decimal import Decimal

from ninja import Schema

from core.schemas import TimestampedSchema


class MetricaIn(Schema):
    """Metric input schema."""

    nome: str
    descricao: str = ""
    tipo_dado: str = "numero"
    ativa: bool = True


class MetricaOut(TimestampedSchema):
    """Metric output schema."""

    id: int
    nome: str
    descricao: str
    tipo_dado: str
    ativa: bool


class MetricaUpdate(Schema):
    """Metric update schema."""

    nome: str | None = None
    descricao: str | None = None
    tipo_dado: str | None = None
    ativa: bool | None = None


class RegistroMetricaIn(Schema):
    """Metric record input schema."""

    metrica_id: int
    valor: Decimal
    data: date
    observacoes: str = ""


class RegistroMetricaOut(TimestampedSchema):
    """Metric record output schema."""

    id: int
    metrica_id: int
    valor: Decimal
    data: date
    observacoes: str
