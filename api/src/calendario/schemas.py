from datetime import datetime

from ninja import Schema

from core.schemas import TimestampedSchema


class EventoIn(Schema):
    """Event input schema."""

    titulo: str
    descricao: str = ""
    data_inicio: datetime
    data_fim: datetime
    local: str = ""
    recorrente: bool = False
    frequencia: str | None = None


class EventoOut(TimestampedSchema):
    """Event output schema."""

    id: int
    titulo: str
    descricao: str
    data_inicio: datetime
    data_fim: datetime
    local: str
    recorrente: bool
    frequencia: str | None


class EventoUpdate(Schema):
    """Event update schema."""

    titulo: str | None = None
    descricao: str | None = None
    data_inicio: datetime | None = None
    data_fim: datetime | None = None
    local: str | None = None
    recorrente: bool | None = None
    frequencia: str | None = None
