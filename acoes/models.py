from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator

from decimal import Decimal


User = get_user_model()


class Acao(models.Model):
    ticker = models.CharField('Ticker', max_length=5, unique=True)
    preco = models.DecimalField(
        'Preço', max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    data_hora_atualizacao = models.DateTimeField(
        'Última atualização', auto_now=True
    )

    class Meta:
        verbose_name_plural = "Ações"
        verbose_name = "Ação"

    def __str__(self):
        return self.ticker


class Carteira(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='carteira_user'
    )
    acao = models.ForeignKey(
        Acao, verbose_name="Ação", on_delete=models.PROTECT,
        related_name='carteira_acao'
    )
    valor_investido = models.DecimalField(
        'Valor investido', max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    preco_medio = models.DecimalField(
        'Preço médio', max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    quantidade = models.PositiveIntegerField('Quantidade')

    class Meta:
        verbose_name_plural = "Carteiras"
        verbose_name = "Carteira"
        ordering = ['acao__ticker']
        unique_together = ('user', 'acao',)

    def calcula_preco_medio_carteira(self, valor_total, quantidade, tipo):
        """
        Calcula preço médio da ação conforme tipo de movimentação
        C - Compra (soma) V - Venda (subtrai)
        """
        if tipo == 'C':
            novo_valor_investido = self.valor_investido + valor_total
            nova_quantidade = self.quantidade + quantidade
            novo_preco_medio = novo_valor_investido / nova_quantidade
            
            return novo_preco_medio, nova_quantidade, novo_valor_investido
        else:
            novo_valor_investido = self.valor_investido - (self.preco_medio * quantidade)
            nova_quantidade = self.quantidade - quantidade

            return self.preco_medio, nova_quantidade, novo_valor_investido

    def __str__(self):
        return 'CARTEIRA: ' + self.user.email + ' AÇÃO: ' + self.acao.ticker


class Movimentacao(models.Model):

    TIPO_MOVIMENTACAO = (
        ('C', 'Compra'),
        ('V', 'Venda')
    )

    acao = models.ForeignKey(
        Acao, verbose_name='Ação',
        on_delete=models.PROTECT,
        related_name='movimentacao_acao'
    )
    data_movimentacao = models.DateField('Data de movimentação')
    tipo = models.CharField('Tipo', choices=TIPO_MOVIMENTACAO, max_length=1)
    preco = models.DecimalField(
        'Preço', max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    preco_medio_venda = models.DecimalField(
        'Preço Médio Venda', max_digits=8, 
        decimal_places=2, blank=True, default=0,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    quantidade = models.PositiveIntegerField(
        'Quantidade', validators=[MinValueValidator(1)]
    )
    valor_total = models.DecimalField(
        'Valor total', max_digits=8, 
        decimal_places=2, default=0, editable=False,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,related_name='movimentacao_user'
    )

    class Meta:
        verbose_name_plural = "Movimentações"
        verbose_name = "Movimentação"

    def __str__(self):
        items = [
            'AÇÃO:',self.acao.ticker,
            'QUANTIDADE:',self.quantidade,
            'VALOR INVESTIDO:', self.valor_total,
            'TIPO:',self.get_tipo_display(),

        ]
        return ' '.join([str(i) for i in items])

    def cria_atualiza_carteira(self):
        """ Atualiza carteira após alteração """
        try:
            acao_carteira = Carteira.objects.get(
                user=self.user, acao=self.acao
            )
        except Carteira.DoesNotExist:
            acao_carteira = None
        
        if acao_carteira:
            (novo_preco_medio,
            nova_quantidade,
            novo_valor_investido) = acao_carteira.calcula_preco_medio_carteira(
                self.valor_total,
                self.quantidade,
                self.tipo,
            )
            if nova_quantidade == 0:
                acao_carteira.delete()
            else:
                acao_carteira.preco_medio = novo_preco_medio
                acao_carteira.quantidade = nova_quantidade
                acao_carteira.valor_investido = novo_valor_investido
                acao_carteira.save()
        else:
            Carteira.objects.create(
                acao = self.acao,
                user = self.user,
                valor_investido = self.valor_total,
                preco_medio = (
                    self.valor_total / self.quantidade
                ),
                quantidade = self.quantidade
            )

@receiver(post_save, sender=Movimentacao)
def after_created_movimentacao(sender, instance, created, **kwargs):
    """ Cria ou atualiza registro na Carteira """
    instance.cria_atualiza_carteira()

@receiver(pre_save, sender=Movimentacao)
def before_created_movimentacao(sender, instance, **kwargs):
    """ Atualiza valor total caso alguma movimentação seja alterada """
    novo_valor_total = instance.quantidade * instance.preco
    instance.valor_total = novo_valor_total