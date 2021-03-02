from django.contrib import admin
from . import models


class VariacaoInLine(admin.TabularInline):
    model = models.Variacao
    # linhas extras da tabela
    extra = 1


class ProdutoAdmin(admin.ModelAdmin):
    #  para poder editar junto com quem ( Produto e a Varicao...)
    inlines = [
        VariacaoInLine
    ]

admin.site.register(models.Produto, ProdutoAdmin)
admin.site.register(models.Variacao)
