from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.http import JsonResponse

from datetime import date

from acoes.models import Carteira, Movimentacao


@login_required
def lucro_prejuizo_mes_chart(request):
    """ Lucro x Prejuizo por mes no ano atual """
    movimentacoes = Movimentacao.objects.filter(
        user=request.user, data_movimentacao__year=date.today().year, tipo='V'
    )

    resultados_por_mes = {}
    for mes in range(1,13):
        resultados_por_mes[mes] = {}
        resultados_por_mes[mes]['lucro'] = 0
        resultados_por_mes[mes]['prejuizo'] = 0

        resultado = movimentacoes.filter(data_movimentacao__month=mes).annotate(
            resultado_venda=F('valor_total')-(Sum(F('preco_medio_venda')*F('quantidade')))
        )

        for i in resultado:
            if i.resultado_venda > 0:
                resultados_por_mes[mes]['lucro'] += i.resultado_venda
            else:
                resultados_por_mes[mes]['prejuizo'] -= i.resultado_venda
    return JsonResponse(data={
        'data': resultados_por_mes,
    })


@login_required
def dashboard(request):
    """ Items do Dashboard """

    # Carteira
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
        'totais': totais,
    }
    return render(request, 'dashboard/dashboard.html', dados)
