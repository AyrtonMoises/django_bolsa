from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

from decimal import Decimal
import json


from acoes.models import Acao, Carteira, Movimentacao


User = get_user_model()


class AcaoCadastroTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url_cadastrar_acao = reverse('cria_acao')
        self.url_login = reverse(settings.LOGIN_URL)
        self.user = User.objects.create_user(
            email='teste@teste.com',
            password='senha_secreta'
        )
        self.acao = Acao.objects.create(
            ticker='COGN3',
            preco=2.14
        )

    def tearDown(self):
        self.user.delete()
        Acao.objects.all().delete()

    def test_view_nao_autenticado(self):
        """ Acesso não autenticado """
        response = self.client.get(self.url_cadastrar_acao)
        self.assertRedirects(response, self.url_login + f"?next={self.url_cadastrar_acao}")

    def test_view_autenticado(self):
        """ Acesso autenticado """
        self.client.login(email=self.user.email, password='senha_secreta')
        response = self.client.get(self.url_cadastrar_acao)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'acao/_form.html')

    def test_cadastrar_acao_ok(self):
        """ Cadastro de acao """
        self.client.login(email=self.user.email, password='senha_secreta')
        data = {
            'ticker': 'VIIA3',
            'preco': 4.00
        }
        response = self.client.post(self.url_cadastrar_acao, data)
        self.assertEquals(response.status_code, 200)

    def test_cadastrar_acao_falha(self):
        """ Cadastro de acao com erro """
        self.client.login(email=self.user.email, password='senha_secreta')
        data = {
            'ticker': 'COGN333',
            'preco': 2222222222222222222.14
        }
        response = self.client.post(self.url_cadastrar_acao, data)
        self.assertEquals(response.status_code, 400)
        self.assertFormError(response, 'form', 'ticker', 
            'Certifique-se de que o valor tenha no máximo 5 caracteres (ele possui 7).'
        )
        self.assertFormError(response, 'form', 'preco', 
            'Certifique-se de que não tenha mais de 8 dígitos no total.',      
        )

    def test_cadastrar_acao_repetida(self):
        """ Cadastro de acao existente """
        self.client.login(email=self.user.email, password='senha_secreta')
        data = {
            'ticker': 'COGN3',
            'preco': 2.14
        }
        response = self.client.post(self.url_cadastrar_acao, data)
        self.assertEquals(response.status_code, 400)
        self.assertFormError(response, 'form', 'ticker', 
            'Ação com este Ticker já existe.'
        )


class MovimentacaoCadastroTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url_cadastro_movimentacao = reverse('cria_movimentacao')
        self.url_login = reverse(settings.LOGIN_URL)
        self.user = User.objects.create_user(
            email='teste@teste.com',
            password='senha_secreta'
        )
        self.acao = Acao.objects.create(
            ticker='COGN3',
            preco=2.14
        )
        self.acao_extra = Acao.objects.create(
            ticker='VIIA3',
            preco=4.00
        )
        self.movimentacao = Movimentacao.objects.create(
            acao=self.acao_extra,
            data_movimentacao='2022-01-17',
            preco=4.00,
            tipo='C',
            quantidade= 100,
            user=self.user
        )

    def tearDown(self):
        self.user.delete()
        Movimentacao.objects.all().delete()
        Carteira.objects.all().delete()

    def test_view_nao_autenticado(self):
        """ Acesso não autenticado """
        response = self.client.get(self.url_cadastro_movimentacao)
        self.assertRedirects(response, 
            self.url_login + f"?next={self.url_cadastro_movimentacao}"
        )

    def test_view_autenticado(self):
        """ Acesso autenticado """
        self.client.login(email=self.user.email, password='senha_secreta')
        response = self.client.get(self.url_cadastro_movimentacao)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'movimentacao/_form.html')

    def test_cadastrar_movimentacao_ok(self):
        """ Cadastro de movimentacao e cadastro em carteira via signals """
        self.client.login(email=self.user.email, password='senha_secreta')
        data = {
            'acao': self.acao.id,
            'data_movimentacao': '2022-01-17',
            'tipo': 'C',
            'preco': 2.14,
            'quantidade': 100
        }
        response = self.client.post(self.url_cadastro_movimentacao, data)
        self.assertEquals(response.status_code, 200)

        carteira = Carteira.objects.filter(
            user=self.user, acao=self.acao
        ).first()
        self.assertEquals(carteira.valor_investido, 214.00)
        self.assertEquals(carteira.preco_medio, Decimal('2.14'))
        self.assertEquals(carteira.quantidade, 100)

    def test_cadastrar_movimentacao_falha_acao(self):
        """ Cadastro de movimentacao de venda sem ação em carteira """
        self.client.login(email=self.user.email, password='senha_secreta')
        data = {
            'acao': self.acao.id,
            'data_movimentacao': '2022-01-17',
            'tipo': 'V',
            'preco': 2.14,
            'quantidade': 10000
        }
        response = self.client.post(self.url_cadastro_movimentacao, data)
        self.assertEquals(response.status_code, 400)
        self.assertFormError(response, 'form', 'acao', 
            'Não existe a ação em carteira para venda!'
        )

    def test_cadastrar_movimentacao_falha_quantidade(self):
        """ 
        Cadastro de movimentacao de venda quantidade diferente em carteira
        """
        self.client.login(email=self.user.email, password='senha_secreta')
        data = {
            'acao': self.acao.id,
            'data_movimentacao': '2022-01-17',
            'tipo': 'C',
            'preco': 2.14,
            'quantidade': 100
        }
        self.client.post(self.url_cadastro_movimentacao, data)

        data = {
            'acao': self.acao.id,
            'data_movimentacao': '2022-01-17',
            'tipo': 'V',
            'preco': 2.14,
            'quantidade': 200
        }
        response = self.client.post(self.url_cadastro_movimentacao, data)
        self.assertEquals(response.status_code, 400)
        self.assertFormError(response, 'form', 'quantidade', 
            'Quantidade em carteira e menor que a de venda!'
        )

    def test_cadastrar_atualiza_carteira_compra(self):
        """ 
        Cadastro de nova compra de ação para atualizar em carteira
        """
        self.client.login(email=self.user.email, password='senha_secreta')
        data = {
            'acao': self.acao_extra.id,
            'data_movimentacao': '2022-01-17',
            'tipo': 'C',
            'preco': 6.50,
            'quantidade': 100
        }
        response = self.client.post(self.url_cadastro_movimentacao, data)
        self.assertEquals(response.status_code, 200)

        carteira = Carteira.objects.filter(
            user=self.user, acao=self.acao_extra
        ).first()
        self.assertEquals(carteira.valor_investido, 1050.00)
        self.assertEquals(carteira.preco_medio, Decimal('5.25'))
        self.assertEquals(carteira.quantidade, 200)

    def test_cadastrar_atualiza_carteira_venda_parcial(self):
        """ 
        Cadastro de nova venda de ação para atualizar em carteira
        """
        self.client.login(email=self.user.email, password='senha_secreta')
        data = {
            'acao': self.acao_extra.id,
            'data_movimentacao': '2022-01-17',
            'tipo': 'V',
            'preco': 6.50,
            'quantidade': 50
        }
        response = self.client.post(self.url_cadastro_movimentacao, data)
        self.assertEquals(response.status_code, 200)

        carteira = Carteira.objects.filter(
            user=self.user, acao=self.acao_extra
        ).first()
        movimento = Movimentacao.objects.filter(user=self.user).last()
        self.assertEquals(movimento.preco_medio_venda, 4.00)
        self.assertEquals(carteira.valor_investido, 200.00)
        self.assertEquals(carteira.preco_medio, Decimal('4.00'))
        self.assertEquals(carteira.quantidade, 50)

    def test_cadastrar_atualiza_carteira_venda_total(self):
        """ 
        Cadastro de nova venda de ação para remover da carteira
        """
        self.client.login(email=self.user.email, password='senha_secreta')
        data = {
            'acao': self.acao_extra.id,
            'data_movimentacao': '2022-01-17',
            'tipo': 'V',
            'preco': 6.50,
            'quantidade': 100
        }
        response = self.client.post(self.url_cadastro_movimentacao, data)
        self.assertEquals(response.status_code, 200)

        carteira = Carteira.objects.filter(
            user=self.user, acao=self.acao_extra
        ).exists()
        self.assertFalse(carteira)

class ListaMovimentacaoTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url_movimentacoes = reverse('movimentacoes')
        self.url_login = reverse(settings.LOGIN_URL)
        self.user = User.objects.create_user(
            email='teste@teste.com',
            password='senha_secreta'
        )
        self.acao = Acao.objects.create(
            ticker='COGN3',
            preco=2.14
        )
        self.acao_extra = Acao.objects.create(
            ticker='VIIA3',
            preco=4.00
        )
        Movimentacao.objects.create(
            acao=self.acao,
            data_movimentacao='2022-01-17',
            preco=2.17,
            tipo='C',
            quantidade= 100,
            user=self.user
        )
        Movimentacao.objects.create(
            acao=self.acao_extra,
            data_movimentacao='2022-01-18',
            preco=4.00,
            tipo='C',
            quantidade= 300,
            user=self.user
        )

    def tearDown(self):
        self.user.delete()
        Movimentacao.objects.all().delete()

    def test_view_nao_autenticado(self):
        """ Acesso não autenticado """
        response = self.client.get(self.url_movimentacoes)
        self.assertRedirects(response, 
            self.url_login + f"?next={self.url_movimentacoes}"
        )

    def test_view_autenticado(self):
        """ Acesso autenticado """
        self.client.login(email=self.user.email, password='senha_secreta')
        response = self.client.get(self.url_movimentacoes)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'movimentacao/_lista.html')
        lista_movimentacoes = response.context['movimentacoes']
        self.assertEquals(lista_movimentacoes.count(), 2)


class DashboardTestCase(TestCase):

    maxDiff = None

    def setUp(self):
        self.client = Client()
        self.url_dashboard = reverse('dashboard')
        self.url_grafico = reverse('lucro_prejuizo_mes_chart')
        self.url_login = reverse(settings.LOGIN_URL)

        self.user = User.objects.create_user(
            email='teste@teste.com',
            password='senha_secreta'
        )
        self.acao = Acao.objects.create(
            ticker='COGN3',
            preco=2.14
        )
        self.acao_extra = Acao.objects.create(
            ticker='VIIA3',
            preco=4.00
        )
        Movimentacao.objects.create(
            acao=self.acao,
            data_movimentacao='2022-01-17',
            preco=2.17,
            tipo='C',
            quantidade= 200,
            user=self.user
        )
        Movimentacao.objects.create(
            acao=self.acao_extra,
            data_movimentacao='2022-01-18',
            preco=4.00,
            tipo='C',
            quantidade= 300,
            user=self.user
        )

    def tearDown(self):
        self.user.delete()
        Movimentacao.objects.all().delete()

    def test_view_nao_autenticado(self):
        """ Acesso não autenticado """
        response = self.client.get(self.url_dashboard)
        self.assertRedirects(response, 
            self.url_login + f"?next={self.url_dashboard}"
        )

    def test_view_autenticado(self):
        """ Acesso autenticado """
        self.client.login(email=self.user.email, password='senha_secreta')
        response = self.client.get(self.url_dashboard)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_cards(self):
        """ Teste dos cards de Total investido, Atual, Lucro/Prejuízo """
        self.client.login(email=self.user.email, password='senha_secreta')
        response = self.client.get(self.url_dashboard)
        totais = response.context['totais']
        self.assertEquals(totais['total_investido'], Decimal('1634.00'))
        self.assertEquals(totais['total_atual'], Decimal('1628.00'))
        self.assertEquals(
            totais['total_atual']-totais['total_investido'], 
            Decimal('-6.00')
        )

    def test_carteira(self):
        """ Teste carteira """
        self.client.login(email=self.user.email, password='senha_secreta')
        response = self.client.get(self.url_dashboard)
        carteira_atual = response.context['carteira']
        self.assertEquals(carteira_atual.count(), 2)

    def test_alocacao(self):
        """ Teste alocacao carteira por acao """
        self.client.login(email=self.user.email, password='senha_secreta')
        response = self.client.get(self.url_dashboard)
        carteira_alocacao = response.context['carteira_alocacao']
        self.assertEquals(carteira_alocacao.count(), 2)

    def test_grafico_lucro(self):
        """ Teste dados json grafico lucro mensal """
        self.client.login(email=self.user.email, password='senha_secreta')

        # Realiza venda no lucro e prejuizo para demonstracao
        data = {
            'acao': self.acao_extra.id,
            'data_movimentacao': '2022-01-17',
            'tipo': 'V',
            'preco': 5.00,
            'quantidade': 100
        }
        self.client.post(reverse('cria_movimentacao'), data)  

        data = {
            'acao': self.acao_extra.id,
            'data_movimentacao': '2022-02-18',
            'tipo': 'V',
            'preco': 2.00,
            'quantidade': 100
        }
        self.client.post(reverse('cria_movimentacao'), data)  

        # Faz request com os resultados
        response = self.client.get(self.url_grafico)
        self.assertEqual(response.status_code, 200)

        dados =  {'data':{
            '1': {'lucro': '100', 'prejuizo': 0},
            '2': {'lucro': 0, 'prejuizo': '200'},
            '3': {'lucro': 0, 'prejuizo': 0},
            '4': {'lucro': 0, 'prejuizo': 0},
            '5': {'lucro': 0, 'prejuizo': 0},
            '6': {'lucro': 0, 'prejuizo': 0},
            '7': {'lucro': 0, 'prejuizo': 0},
            '8': {'lucro': 0, 'prejuizo': 0},
            '9': {'lucro': 0, 'prejuizo': 0},
            '10': {'lucro': 0, 'prejuizo': 0},
            '11': {'lucro': 0, 'prejuizo': 0},
            '12': {'lucro': 0, 'prejuizo': 0}
          }}
        dados = json.dumps(dados)
        self.assertJSONEqual(str(response.content, encoding='utf8'), dados)

