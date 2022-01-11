from django.contrib import admin

from .models import Acao, Movimentacao, Carteira


admin.site.register([Acao, Movimentacao, Carteira])