from datetime import date

from ninja import Schema

from core.schemas import TimestampedSchema


class HabitoIn(Schema):
    """Habit input schema."""

    nome: str
    descricao: str = ""
    frequencia_desejada: int = 1
    ativo: bool = True


class HabitoOut(TimestampedSchema):
    """Habit output schema."""

    id: int
    nome: str
    descricao: str
    frequencia_desejada: int
    ativo: bool


class HabitoUpdate(Schema):
    """Habit update schema."""

    nome: str | None = None
    descricao: str | None = None
    frequencia_desejada: int | None = None
    ativo: bool | None = None


class RegistroHabitoIn(Schema):
    """Habit record input schema."""

    habito_id: int
    data: date
    observacoes: str = ""


class RegistroHabitoOut(TimestampedSchema):
    """Habit record output schema."""

    id: int
    habito_id: int
    data: date
    observacoes: str
