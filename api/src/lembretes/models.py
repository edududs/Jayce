from django.db import models

from core.models import UserOwnedModel


class Lembrete(UserOwnedModel):
    """Reminder model."""

    class Prioridade(models.TextChoices):
        BAIXA = "baixa", "Baixa"
        MEDIA = "media", "Média"
        ALTA = "alta", "Alta"

    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    data_hora = models.DateTimeField()
    concluido = models.BooleanField(default=False)
    prioridade = models.CharField(
        max_length=10,
        choices=Prioridade.choices,
        default=Prioridade.MEDIA,
    )

    class Meta:
        ordering = ["data_hora"]
        verbose_name = "Lembrete"
        verbose_name_plural = "Lembretes"

    def __str__(self) -> str:
        return self.titulo
