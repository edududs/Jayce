from datetime import date

from ninja import Schema

from core.schemas import TimestampedSchema


class ProjetoIn(Schema):
    """Project input schema."""

    nome: str
    descricao: str = ""
    status: str = "planejamento"
    data_inicio: date | None = None
    data_fim: date | None = None
    data_limite: date | None = None


class ProjetoOut(TimestampedSchema):
    """Project output schema."""

    id: int
    nome: str
    descricao: str
    status: str
    data_inicio: date | None
    data_fim: date | None
    data_limite: date | None


class ProjetoUpdate(Schema):
    """Project update schema."""

    nome: str | None = None
    descricao: str | None = None
    status: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    data_limite: date | None = None


class TarefaProjetoIn(Schema):
    """Project task input schema."""

    projeto_id: int
    titulo: str
    descricao: str = ""
    ordem: int = 0


class TarefaProjetoOut(TimestampedSchema):
    """Project task output schema."""

    id: int
    projeto_id: int
    titulo: str
    descricao: str
    concluida: bool
    ordem: int


class TarefaProjetoUpdate(Schema):
    """Project task update schema."""

    titulo: str | None = None
    descricao: str | None = None
    concluida: bool | None = None
    ordem: int | None = None
