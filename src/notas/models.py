from django.db import models

from core.models import TimestampedModel, UserOwnedModel


class NotaTag(TimestampedModel):
    """Note tag model."""

    tag = models.CharField(max_length=200)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Tag da Nota"
        verbose_name_plural = "Tags da Nota"

    def __str__(self) -> str:
        return self.tag


class Nota(UserOwnedModel):
    """Note model."""

    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    arquivada = models.BooleanField(default=False)
    tags = models.ManyToManyField(NotaTag, related_name="notas", blank=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Nota"
        verbose_name_plural = "Notas"

    def __str__(self) -> str:
        return self.titulo
