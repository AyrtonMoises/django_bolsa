from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from acoes.models import Carteira, Movimentacao
from acoes.forms import MovimentacaoForm, AcaoForm


@login_required
@csrf_exempt
def cria_movimentacao(request):
    """ Cria movimentação """
    form = MovimentacaoForm(request.POST or None, request=request)

    if request.method == 'POST':
        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.user = request.user
            if movimentacao.tipo == 'V':
                acao_carteira_user = Carteira.objects.get(
                    user=request.user, acao=movimentacao.acao
                )
                movimentacao.preco_medio_venda = acao_carteira_user.preco_medio
            movimentacao.save()
            return HttpResponse('ok')
        else:
            return render(
                request, 'movimentacao/_form.html', {'form': form}, status=400
            )

    return render(request, 'movimentacao/_form.html', {'form': form})

@login_required
@csrf_exempt
def cria_acao(request):
    """ Cria ação """
    form = AcaoForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponse('ok')
        else:
            return render(
                request, 'acao/_form.html', {'form': form}, status=400
            )

    return render(request, 'acao/_form.html', {'form': form})

@login_required
@csrf_exempt
def movimentacoes(request):
    """ Lista movimentações do usuário """
    movimentacoes = Movimentacao.objects.filter(user=request.user).order_by('-data_movimentacao')
    dados = {
        'movimentacoes': movimentacoes
    }
    return render(request, 'movimentacao/_lista.html', dados)
