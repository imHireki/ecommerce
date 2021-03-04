from django.shortcuts import render
from django.views.generic.list import ListView
from django.views import View
from django.http import HttpResponse


class ListaProdutos(ListView):
    def get(self, *args, **kwargs):
        return HttpResponse('ListaProdutos')


class DetalheProduto(View):
    def get(self, *args, **kwargs):
        return HttpResponse('DetalheProduto')


class AdicionarAoCarrinho(View):
    def get(self, *args, **kwargs):
        return HttpResponse('AdicionarAocarrinho')


class RemoverDoCarrinho(View):
    def get(self, *args, **kwargs):
        return HttpResponse('RemoverdoCarrinho')


class Carrinho(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Carrinho')


class Finalizar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Finalizar')
