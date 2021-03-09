from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views import View
from django.http import HttpResponse, request
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import copy
from . import models
from . import forms


class BasePerfil(View):
    template_name = 'perfil/criar.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        
        # copiando carrinho para variavel para não perder quando trocar senha 
        self.carrinho = copy.deepcopy(self.request.session.get('carrinho', {}))

        self.perfil = None
        
        if self.request.user.is_authenticated:
            self.perfil = models.Perfil.objects.filter(
                usuario=self.request.user
            ).first()
            
            self.contexto = {
                'userform': forms.UserForm(
                    data=self.request.POST or None,
                    usuario=self.request.user,
                    instance=self.request.user
                ),
                'perfilform': forms.PerfilForm(
                    data=self.request.POST or None,
                    instance=self.perfil
                )
            }
        else:
            self.contexto = {
                'userform': forms.UserForm(
                    data=self.request.POST or None
                ),
                'perfilform': forms.PerfilForm(
                    data=self.request.POST or None
                )
            }
            
        """
        self.contexto
        {
            'userform': <UserForm bound=True, valid=False,
            fields=(first_name;last_name;username;password;password2;email)>,
        
            'perfilform': <PerfilForm bound=True, valid=Unknown,
        
            fields=(
                idade;data_nascimento;cpf;endereco;numero;
                complemento;bairro;cep;cidade;estado
            )>
        }
        """
        
        self.userform = self.contexto['userform']
        self.perfilform = self.contexto['perfilform']  
        
        if self.request.user.is_authenticated:
            self.template_name = 'perfil/atualizar.html'

        self.renderizar = render(
            self.request, self.template_name, self.contexto)

    def get(self, *args, **kwargs):
        return self.renderizar


class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        if not self.userform.is_valid() or not self.perfilform.is_valid():
            return self.renderizar

        username = self.userform.cleaned_data.get('username')
        password = self.userform.cleaned_data.get('password')
        email = self.userform.cleaned_data.get('email')
        first_name = self.userform.cleaned_data.get('first_name')
        last_name = self.userform.cleaned_data.get('last_name')
        
        # Usuário logado
        if self.request.user.is_authenticated:
            usuario = get_object_or_404(User, username=self.request.user.username)
            
            usuario.username = username
            
            if password:
                # não pode passar direto por precisar da criptografia
                usuario.set_password(password)
                
            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.save()
            
            if not self.perfil:
                self.perfilform.cleaned_data['usuario'] = usuario
                perfil = models.Perfil(**self.perfilform.cleaned_data)
                perfil.save()
            else:
                self.perfilform.save(commit=False)
                perfil.usuario = usuario
                perfil.save()
            
        #  Usuário não logado (novo)
        else:
            # registra um usuario e um perfil para o usuario
            usuario = self.userform.save(commit=False)
            usuario.set_password(password)
            usuario.save()
            
            perfil = self.perfilform.save(commit=False)
            perfil.usuario = usuario
            perfil.save()
            # autentica um usuário e passa ele para um nova seção
        
        if password:
            autentica = authenticate(
                self.request,
                username=usuario,
                password=password
            )
            
            if autentica:
                login(self.request, user=usuario)
                
        self.request.session['carrinho'] = self.carrinho
        self.request.session.save()
        
        messages.success(
            self.request,
            'Seu cadastro foi criado ou atualizado com sucesso'
        )
        
        messages.success(
            self.request,
            'Você fez login e pode concluir sua compra'
        )
        
        return redirect('perfil:criar')

class Atualizar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Atualizar')


class Login(View):
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')

        if not username or not password:
            messages.error(
                self.request,
                'Usuário ou senha inválidos'
            )
            return redirect('perfil:criar')
        
        usuario = authenticate(
            self.request, username=username, password=password
        )

        if not usuario:
            messages.error(
                self.request,
                'Usuário ou senha inválidos'
            )
            return redirect('perfil:criar')
        
        login(self.request, user=usuario)
        
        messages.success(
            self.request,
            'Você fez login no sistema e pode concluir sua compra'
        )
        return redirect('produto:carrinho')
        
        
class Logout(View):
    def get(self, *args, **kwargs):
        # para não perder o carrinho
        carrinho = copy.deepcopy(self.request.session.get('carrinho'))

        logout(self.request)
        
        # não perder o carrinho 2 
        self.request.session['carrinho'] = carrinho
        self.request.session.save()        
        return redirect('produto:lista')
