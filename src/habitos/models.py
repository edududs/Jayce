from django.db import models

from core.models import UserOwnedModel


class Habito(UserOwnedModel):
    """Habit model."""

    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    frequencia_desejada = models.IntegerField(default=1, help_text="Vezes por semana")
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Hábito"
        verbose_name_plural = "Hábitos"

    def __str__(self) -> str:
        return self.nome


class RegistroHabito(UserOwnedModel):
    """Habit tracking record."""

    habito = models.ForeignKey(Habito, on_delete=models.CASCADE, related_name="registros")
    data = models.DateField()
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ["-data"]
        unique_together = [["habito", "data"]]
        verbose_name = "Registro de Hábito"
        verbose_name_plural = "Registros de Hábitos"

    def __str__(self) -> str:
        return f"{self.habito.nome} - {self.data}"
