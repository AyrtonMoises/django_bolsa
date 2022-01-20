from django import forms

from .models import Movimentacao, Acao
from .validations import (
    valida_acao_existe_carteira, valida_quantidade_carteira
)


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
            'class': "form-control",
            'min': 0.01,
        })
    )
    quantidade = forms.IntegerField(
        required=True,
        label='Quantidade',
        widget=forms.NumberInput(attrs={
            'class': "form-control",
            'min': 1,
        })
    )

    def __init__(self, *args, **kwargs):
        """ Modifica classe para receber request com o user """
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def clean(self):
        """ Valida campos antes de inserir """
        acao = self.cleaned_data.get('acao')
        tipo = self.cleaned_data.get('tipo')
        quantidade = self.cleaned_data.get('quantidade')
        usuario = self.request.user
        campos_com_erro = {}

        if tipo == 'V':
            valida_acao_existe_carteira(acao, usuario, campos_com_erro)
            valida_quantidade_carteira(acao, usuario, quantidade, campos_com_erro)
        if campos_com_erro:
            for campo, mensagem in campos_com_erro.items():
                self.add_error(campo, mensagem)

        return self.cleaned_data

    class Meta:
        model = Movimentacao
        exclude = ['user','valor_total','preco_medio_venda']


class AcaoForm(forms.ModelForm):
    ticker = forms.CharField(
        required=True,
        label='Ticker',
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'maxlength': 5,
            'minlength': 5,
            'style' : "text-transform:uppercase"
        })
    )

    preco = forms.DecimalField(
        label='Preço',
        required=True,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': "form-control",
            'min': 0.01,
        })
    )

    def clean_ticker(self):
        """ Deixa ticker em letras maiúsculas """
        ticker = self.cleaned_data.get('ticker')
        if not len(ticker) == 5:
            raise forms.ValidationError("Ticker deve ter tamanho de 5 caracteres")
        ticker = ticker.upper()
        return ticker

    class Meta:
        model = Acao
        exclude = ['data_hora_atualizacao',]