from django.db import models

from core.models import UserOwnedModel


class Tarefa(UserOwnedModel):
    """Task model."""

    class Prioridade(models.TextChoices):
        BAIXA = "baixa", "Baixa"
        MEDIA = "media", "Média"
        ALTA = "alta", "Alta"

    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    concluida = models.BooleanField(default=False)
    prioridade = models.CharField(
        max_length=10,
        choices=Prioridade.choices,
        default=Prioridade.MEDIA,
    )
    data_vencimento = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"

    def __str__(self) -> str:
        return self.titulo
