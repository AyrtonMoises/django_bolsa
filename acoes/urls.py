from django.urls import path

from .views import (cria_movimentacao, movimentacoes, cria_acao,
dashboard, lucro_prejuizo_mes_chart)


urlpatterns = [
    path('movimentacao/criar', cria_movimentacao, name="cria_movimentacao"),
    path('movimentacoes/', movimentacoes, name="movimentacoes"),
    path('acao/criar', cria_acao, name="cria_acao"),
    path('dashboard/', dashboard, name="dashboard"),
    path('lucro_prejuizo_mes_chart/', lucro_prejuizo_mes_chart, name="lucro_prejuizo_mes_chart"),
]
