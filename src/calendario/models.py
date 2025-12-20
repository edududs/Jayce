from django.db import models

from core.models import UserOwnedModel


class Evento(UserOwnedModel):
    """Calendar event model."""

    class Frequencia(models.TextChoices):
        DIARIA = "diaria", "Diária"
        SEMANAL = "semanal", "Semanal"
        MENSAL = "mensal", "Mensal"
        ANUAL = "anual", "Anual"

    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    local = models.CharField(max_length=200, blank=True)
    recorrente = models.BooleanField(default=False)
    frequencia = models.CharField(
        max_length=20,
        choices=Frequencia.choices,
        blank=True,
    )

    class Meta:
        ordering = ["data_inicio"]
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"

    def __str__(self) -> str:
        return self.titulo
