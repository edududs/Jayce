from django.db import models

from core.models import UserOwnedModel


class Metrica(UserOwnedModel):
    """Metric/analysis model."""

    class TipoDado(models.TextChoices):
        NUMERO = "numero", "Número"
        PORCENTAGEM = "porcentagem", "Porcentagem"
        TEMPO = "tempo", "Tempo"
        TEXTO = "texto", "Texto"

    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    tipo_dado = models.CharField(
        max_length=20,
        choices=TipoDado.choices,
        default=TipoDado.NUMERO,
    )
    ativa = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Métrica"
        verbose_name_plural = "Métricas"

    def __str__(self) -> str:
        return self.nome


class RegistroMetrica(UserOwnedModel):
    """Metric record/measurement."""

    metrica = models.ForeignKey(Metrica, on_delete=models.CASCADE, related_name="registros")
    valor = models.DecimalField(max_digits=15, decimal_places=4)
    data = models.DateField()
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ["-data"]
        verbose_name = "Registro de Métrica"
        verbose_name_plural = "Registros de Métricas"

    def __str__(self) -> str:
        return f"{self.metrica.nome} - {self.data}: {self.valor}"
