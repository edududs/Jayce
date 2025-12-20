from datetime import datetime
from typing import Optional

from ninja import Schema
from pydantic import ConfigDict


class BaseSchema(Schema):
    """Classe base centralizada para configuração."""

    model_config = ConfigDict(from_attributes=True)


class TimestampedSchema(BaseSchema):
    """Base schema com timestamps automáticos."""

    created_at: datetime
    updated_at: datetime


class ResponseSchema[T](BaseSchema):
    """Wrapper genérico seguindo padrões modernos do Pydantic v2."""

    data: T
    message: Optional[str] = None


class ErrorSchema(BaseSchema):
    """Schema de erro padronizado."""

    detail: str
    code: Optional[str] = None
