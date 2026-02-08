from datetime import datetime

from ninja import Schema

from core.schemas import TimestampedSchema


class LembreteIn(Schema):
    """Reminder input schema."""

    titulo: str
    descricao: str = ""
    data_hora: datetime
    prioridade: str = "media"


class LembreteOut(TimestampedSchema):
    """Reminder output schema."""

    id: int
    titulo: str
    descricao: str
    data_hora: datetime
    concluido: bool
    prioridade: str


class LembreteUpdate(Schema):
    """Reminder update schema."""

    titulo: str | None = None
    descricao: str | None = None
    data_hora: datetime | None = None
    concluido: bool | None = None
    prioridade: str | None = None
