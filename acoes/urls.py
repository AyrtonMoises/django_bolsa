from django.urls import path

from .views import cria_movimentacao


urlpatterns = [
    path('movimentacao/criar', cria_movimentacao, name="cria_movimentacao"),
]
