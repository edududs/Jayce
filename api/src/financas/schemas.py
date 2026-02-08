from datetime import date
from decimal import Decimal

from ninja import Schema

from core.schemas import TimestampedSchema


class TransacaoIn(Schema):
    """Transaction input schema."""

    descricao: str
    valor: Decimal
    tipo: str
    categoria: str
    data: date
    observacoes: str = ""


class TransacaoOut(TimestampedSchema):
    """Transaction output schema."""

    id: int
    descricao: str
    valor: Decimal
    tipo: str
    categoria: str
    data: date
    observacoes: str


class TransacaoUpdate(Schema):
    """Transaction update schema."""

    descricao: str | None = None
    valor: Decimal | None = None
    tipo: str | None = None
    categoria: str | None = None
    data: date | None = None
    observacoes: str | None = None
