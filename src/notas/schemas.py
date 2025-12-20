from ninja import Schema
from pydantic import field_validator

from core.schemas import TimestampedSchema


class NotaTagOut(TimestampedSchema):
    """Note tag output schema."""

    id: int
    tag: str


class NotaIn(Schema):
    """Note input schema."""

    titulo: str
    conteudo: str
    tags: str = ""
    arquivada: bool = False

    @classmethod
    @field_validator("tags", mode="before")
    def validate_tags(cls, v: str) -> list[str]:
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(",")]
        return v


class NotaOut(TimestampedSchema):
    """Note output schema."""

    id: int
    titulo: str
    conteudo: str
    tags: list[NotaTagOut]
    arquivada: bool


class NotaUpdate(Schema):
    """Note update schema."""

    titulo: str | None = None
    conteudo: str | None = None
    tags: str | None = None
    arquivada: bool | None = None
