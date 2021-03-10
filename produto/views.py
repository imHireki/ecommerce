from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.contrib import messages
from django.http import HttpResponse
from . import models
from perfil.models import Perfil


class ListaProdutos(ListView):
    model = models.Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'
    paginate_by = 4


class DetalheProduto(DetailView):
    model = models.Produto
    template_name = 'produto/detalhe.html'
    context_object_name = 'produto'
    # usar o slug do model como url
    slug_url_kwarg = 'slug'


class AdicionarAoCarrinho(View):
    # quando class View, adicionar get e post
    def get(self, *args, **kwargs):
        # if self.request.session.get('carrinho'):
        #     del self.request.session['carrinho']
        #     self.request.session.save()
            
        # link de onde o usuário veio
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )

        # string do id da variação "?vid=15" 15
        variacao_id = self.request.GET.get('vid')

        if not variacao_id:
            messages.error(
                self.request,
                'Produto não existe'
            )
            return redirect(http_referer)

        variacao = get_object_or_404(models.Variacao, id=variacao_id)
        variacao_estoque = variacao.estoque
        produto = variacao.produto

        produto_id = produto.id
        produto_nome = produto.nome
        variacao_nome = variacao.nome or ''
        # variacao_id = variacao.id
        preco_unitario = variacao.preco
        preco_unitario_promocional = variacao.preco_promocional
        quantidade = 1
        slug = produto.slug
        imagem = produto.imagem

        # para retornar apenas o nome
        if imagem:
            imagem = imagem.name
        else:
            imagem = ''

        # garante que todas variações tenham um produto em estoque
        if variacao.estoque < 1:
            messages.error(
                self.request,
                'Estoque Insuficiente'
            )
            return redirect(http_referer)

        # Cria o carrinho na sessão dos settings q dura 7 dias
        if not self.request.session.get('carrinho'):
            self.request.session['carrinho'] = {}
            self.request.session.save()

        carrinho = self.request.session['carrinho']

        if variacao_id in carrinho:
            quantidade_carrinho = carrinho[variacao_id]['quantidade']
            quantidade_carrinho += 1

            if variacao_estoque < quantidade_carrinho:
                messages.warning(
                    self.request,
                    f'Estoque insuficiente para {quantidade_carrinho}x no '
                    f'produto "{produto_nome}". Adicionamos {variacao_estoque}x '
                    f'no seu carrinho'
                )
                quantidade_carrinho = variacao_estoque

            carrinho[variacao_id]['quantidade'] = quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo'] = preco_unitario * \
                quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo_promocional'] = preco_unitario_promocional * \
                quantidade_carrinho
        else:
            carrinho[variacao_id] = {
                'produto_id': produto_id,
                'produto_nome': produto_nome,
                'variacao_nome': variacao_nome,
                'variacao_id': variacao_id,
                'preco_unitario': preco_unitario,
                'preco_unitario_promocional': preco_unitario_promocional,
                'preco_quantitativo': preco_unitario,
                'preco_quantitativo_promocional': preco_unitario_promocional,
                'quantidade': 1,
                'slug': slug,
                'imagem': imagem,
            }

        # para salvar a seção
        self.request.session.save()

        messages.success(
            self.request,
            f'Produto {produto_nome} {variacao_nome} adicionado ao seu carrinho '
            f'carrinho {carrinho[variacao_id]["quantidade"]}x'
        )
        
        return redirect(http_referer)


class RemoverDoCarrinho(View):
    def get(self, *args, **kwargs):
        # link de onde o usuário veio
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )

        # string do id da variação "?vid=15" 15
        variacao_id = self.request.GET.get('vid')
        
        if not variacao_id:
            return redirect(http_referer)
        
        if not self.request.session.get('carrinho'):
            return redirect(http_referer)
        
        if variacao_id not in self.request.session['carrinho']:
            return redirect(http_referer)
        
        carrinho = self.request.session['carrinho'][variacao_id]
        
        messages.success(
            self.request,
            f'Produto {carrinho["produto_nome"]} {carrinho["variacao_nome"]} '
            f'removido do seu carrinho'
        )
        
        del self.request.session['carrinho'][variacao_id]
        self.request.session.save()
        return redirect(http_referer)


class Carrinho(View):
    def get(self, *args, **kwargs):
        contexto = {
            'carrinho': self.request.session.get('carrinho', {})
        }

        return render(self.request, 'produto/carrinho.html', contexto)


class ResumoDaCompra(View):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')
        
        perfil = Perfil.objects.filter(usuario=self.request.user).exists()
        
        if not perfil:
            messages.error(
                self.request,
                'Usuário sem perfil'
            )
            return redirect('perfil:criar')
        
        if not self.request.session.get('carrrinho'):
            messages.error(
                self.request,
                'Carrinho vazio'
            )
            return redirect('perfil:criar')       
        
        contexto = {
            'usuario': self.request.user,
            'carrinho': self.request.session['carrinho'],
            
            
        }
        return render(self.request, 'produto/resumodacompra.html', context=contexto)
