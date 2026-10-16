from django.contrib.auth import views as auth_views
from django.urls import path

from . import views, views_anp

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('quem-somos/', views.quem_somos, name='quem_somos'),
    path('informacoes-anp/', views.informacoes_anp, name='informacoes_anp'),
    # Histórico de movimentação (público, somente leitura). Ainda sem link no menu.
    path('informacoes-anp/historico-de-movimentacao/', views_anp.historico_publico, name='historico_movimentacao'),
    path('informacoes-anp/historico-de-movimentacao/historico-movimentacao.xlsx', views_anp.historico_publico_xlsx,
         name='historico_movimentacao_xlsx'),
    path('informacoes-anp/historico-de-movimentacao/historico-movimentacao.csv', views_anp.historico_publico_csv,
         name='historico_movimentacao_csv'),
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

    # Gestão do histórico de movimentação ANP: sem link no menu, acesso pelo endereço direto.
    path('movimentacao-anp/', views_anp.painel, name='anp_painel'),
    path('movimentacao-anp/lancamento/', views_anp.lancamento, name='anp_lancamento'),
    path('movimentacao-anp/lancamento/<str:mes>/', views_anp.lancamento, name='anp_lancamento_mes'),
    path('movimentacao-anp/importar/', views_anp.importar, name='anp_importar'),
    path('movimentacao-anp/exportar.xlsx', views_anp.exportar_xlsx, name='anp_exportar_xlsx'),
    path('movimentacao-anp/exportar.csv', views_anp.exportar_csv, name='anp_exportar_csv'),

    # Endereços do antigo portfólio (conteúdo de demonstração do tema WordPress)
    path('portfolio/<slug:slug>/', views.legacy_portfolio),
    path('portfolio-category/<slug:slug>/', views.legacy_portfolio),
]
