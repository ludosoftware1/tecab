from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('quem-somos/', views.quem_somos, name='quem_somos'),
    path('informacoes-anp/', views.informacoes_anp, name='informacoes_anp'),
    path('contato/', views.contato, name='contato'),
    path('canal-de-integridade/', views.canal_integridade, name='canal_integridade'),
    path('canal-de-integridade/enviado/', views.canal_integridade_enviado, name='canal_integridade_enviado'),

    # Área do Colaborador
    path('area-do-colaborador/', views.area_colaborador, name='area_colaborador'),
    path('area-do-colaborador/alterar-senha/', views.AlterarSenhaView.as_view(), name='alterar_senha'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('sair/', auth_views.LogoutView.as_view(), name='logout'),
    path('registrar/', views.registrar, name='registrar'),
    path('recuperar-senha/', views.RecuperarSenhaView.as_view(), name='recuperar_senha'),
    path('recuperar-senha/enviado/', views.RecuperarSenhaEnviadoView.as_view(), name='recuperar_senha_enviado'),
    path('redefinir-senha/<uidb64>/<token>/', views.RedefinirSenhaView.as_view(), name='redefinir_senha'),
    path('redefinir-senha/concluido/', views.RedefinirSenhaConcluidoView.as_view(), name='redefinir_senha_concluido'),

    # Endereços do antigo portfólio (conteúdo de demonstração do tema WordPress)
    path('portfolio/<slug:slug>/', views.legacy_portfolio),
    path('portfolio-category/<slug:slug>/', views.legacy_portfolio),
]
