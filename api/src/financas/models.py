from django.db import models

from core.models import UserOwnedModel


class Transacao(UserOwnedModel):
    """Financial transaction model."""

    class Tipo(models.TextChoices):
        RECEITA = "receita", "Receita"
        DESPESA = "despesa", "Despesa"

    class Categoria(models.TextChoices):
        ALIMENTACAO = "alimentacao", "Alimentação"
        TRANSPORTE = "transporte", "Transporte"
        MORADIA = "moradia", "Moradia"
        SAUDE = "saude", "Saúde"
        EDUCACAO = "educacao", "Educação"
        LAZER = "lazer", "Lazer"
        OUTROS = "outros", "Outros"

    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    data = models.DateField()
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ["-data", "-created_at"]
        verbose_name = "Transação"
        verbose_name_plural = "Transações"

    def __str__(self) -> str:
        return f"{self.tipo}: {self.descricao} - R$ {self.valor}"
