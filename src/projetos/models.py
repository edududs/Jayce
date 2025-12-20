from django.db import models

from core.models import UserOwnedModel


class Projeto(UserOwnedModel):
    """Project model."""

    class Status(models.TextChoices):
        PLANEJAMENTO = "planejamento", "Planejamento"
        EM_ANDAMENTO = "em_andamento", "Em Andamento"
        PAUSADO = "pausado", "Pausado"
        CONCLUIDO = "concluido", "Concluído"
        CANCELADO = "cancelado", "Cancelado"

    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANEJAMENTO)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    data_limite = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"

    def __str__(self) -> str:
        return self.nome


class TarefaProjeto(UserOwnedModel):
    """Project task model."""

    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name="tarefas")
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    concluida = models.BooleanField(default=False)
    ordem = models.IntegerField(default=0)

    class Meta:
        ordering = ["ordem", "-created_at"]
        verbose_name = "Tarefa do Projeto"
        verbose_name_plural = "Tarefas do Projeto"

    def __str__(self) -> str:
        return f"{self.projeto.nome} - {self.titulo}"
