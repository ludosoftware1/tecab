from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('quem-somos/', views.page, {'name': 'quem_somos'}, name='quem_somos'),
    path('informacoes-anp/', views.page, {'name': 'informacoes_anp'}, name='informacoes_anp'),
    path('area-do-colaborador/', views.page, {'name': 'area_colaborador'}, name='area_colaborador'),
    path('contato/', views.contato, name='contato'),
    path('portfolio/<slug:slug>/', views.portfolio_item, name='portfolio_item'),
    path('portfolio-category/<slug:slug>/', views.portfolio_category, name='portfolio_category'),

    path('login/', views.LoginView.as_view(), name='login'),
    path('sair/', auth_views.LogoutView.as_view(), name='logout'),
    path('registrar/', views.registrar, name='registrar'),
    path('recuperar-senha/', views.RecuperarSenhaView.as_view(), name='recuperar_senha'),
    path('recuperar-senha/enviado/', views.RecuperarSenhaEnviadoView.as_view(), name='recuperar_senha_enviado'),
    path('redefinir-senha/<uidb64>/<token>/', views.RedefinirSenhaView.as_view(), name='redefinir_senha'),
    path('redefinir-senha/concluido/', views.RedefinirSenhaConcluidoView.as_view(), name='redefinir_senha_concluido'),
]
