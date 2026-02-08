from datetime import datetime

from ninja import Schema

from core.schemas import TimestampedSchema


class TarefaIn(Schema):
    """Task input schema."""

    titulo: str
    descricao: str = ""
    prioridade: str = "media"
    data_vencimento: datetime | None = None


class TarefaOut(TimestampedSchema):
    """Task output schema."""

    id: int
    titulo: str
    descricao: str
    concluida: bool
    prioridade: str
    data_vencimento: datetime | None


class TarefaUpdate(Schema):
    """Task update schema."""

    titulo: str | None = None
    descricao: str | None = None
    concluida: bool | None = None
    prioridade: str | None = None
    data_vencimento: datetime | None = None
