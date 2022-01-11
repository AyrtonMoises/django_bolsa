from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .forms import MovimentacaoForm


@csrf_exempt
def cria_movimentacao(request):
    """ Cria movimentação """
    form = MovimentacaoForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.user = request.user
            movimentacao.save()
            return redirect('dashboard')
        else:
            return render(request, 'movimentacao/_form.html', {'form': form}, status=400)

    return render(request, 'movimentacao/_form.html', {'form': form})
