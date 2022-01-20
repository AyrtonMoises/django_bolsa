from django.contrib import admin

from .models import Acao, Carteira, Movimentacao


admin.site.register([Acao, Carteira, Movimentacao])