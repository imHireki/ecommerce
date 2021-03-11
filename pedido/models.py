from django.db import models
from django.contrib.auth.models import User


class Pedido(models.Model):
    # se apago o usuario o item do pedido tbm deve ser apagado
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    total = models.FloatField()  # sem argumento == obrigatório
    qtd_total = models.PositiveIntegerField()
    status = models.CharField(  # charfield com choices para choices
        default="C",
        max_length=1,  # uma letra
        choices=(  # tupla te tuplas
            ('A', 'Aprovado'),
            ('C', 'Criado'),
            ('R', 'Reprovado'),
            ('P', 'Pendente'),
            ('E', 'Enviado'),
            ('F', 'Finalizado')
        )
    )
    
    def __str__(self):
        return f'Pedido n. {self.pk}'
    

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    produto = models.CharField(max_length=255)
    produto_id = models.PositiveIntegerField()
    variacao = models.CharField(max_length=255)
    variacao_id = models.PositiveIntegerField()
    preco = models.FloatField()
    preco_promocional = models.FloatField(default=0)
    quantidade = models.PositiveIntegerField()
    imagem = models.CharField(max_length=2000)  # nome da imagem

    def __str__(self):
        return f'Item do {self.pedido}'

    class Meta:
        verbose_name = 'Item do pedido'
        verbose_name_plural = 'Itens do pedido'
        