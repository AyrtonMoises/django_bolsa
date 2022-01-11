from django import forms

from .models import Movimentacao, Acao


class MovimentacaoForm(forms.ModelForm):
    acao = forms.ModelChoiceField(
        label='Ação',
        required=True,
        queryset=Acao.objects.all(),
        widget=forms.Select(attrs={
            'class': "form-control"
        }),
        initial=0
    )
    data_movimentacao = forms.DateField(
        label='Data de movimentação',
        required=True,
        widget=forms.DateInput(attrs={
            'class': "form-control",
            'type': "date"
        })
    )
    tipo = forms.ChoiceField(
        label='Tipo',
        choices=Movimentacao.TIPO_MOVIMENTACAO,
        required=True,
        widget=forms.Select(attrs={
            'class': "form-control"
        })
    )
    preco = forms.DecimalField(
        label='Preço',
        required=True,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': "form-control"
        })
    )
    quantidade = forms.IntegerField(
        required=True,
        label='Quantidade',
        widget=forms.NumberInput(attrs={
            'class': "form-control"
        })
    )

    class Meta:
        model = Movimentacao
        exclude = ['user','valor_total',]

