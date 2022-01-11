from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum

from acoes.models import Carteira


@login_required
def dashboard(request):
    """ Items do Dashboard """
    carteira = Carteira.objects.filter(
        user=request.user
    )
    acoes_carteira = carteira.annotate(
        lucro=((F('acao__preco')-F('preco_medio'))*F('quantidade')),
        valor_atual=(F('acao__preco')*F('quantidade'))
    )

    totais = carteira.aggregate(
        total_investido=Sum('valor_investido'),
        total_atual=Sum(F('acao__preco')*F('quantidade'))
    )

    dados = {
        'carteira': acoes_carteira,
        'carteira_alocacao': acoes_carteira.order_by('-valor_atual'),
        'totais': totais
    }
    return render(request, 'dashboard/dashboard.html', dados)
