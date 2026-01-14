from django.urls import path, include
from . import views 

urlpatterns = [
    path('healthz/', views.healthz_view, name='healthz'),
    path('health/', views.healthcheck, name='healthcheck'),
    path('', views.index, name='index'),
    path('clientes/', views.clientes, name='clientes'),
    path('transacoes/', views.transacoes, name='transacoes'),
    path('campanhas/', views.campanhas, name='campanhas'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
    path('configuracoes/estabelecimento/', views.configuracoes_estabelecimento, name='configuracoes_estabelecimento'),
    path('configuracoes/regra-padrao/', views.configuracoes_regra_padrao, name='configuracoes_regra_padrao'),
    path('ajuda/', views.ajuda_home, name='ajuda_home'),
    path('ajuda/<str:slug>/', views.ajuda_guia, name='ajuda_guia'),
    path('creditar-moedas/', views.creditar_moedas, name='creditar_moedas'),
]
