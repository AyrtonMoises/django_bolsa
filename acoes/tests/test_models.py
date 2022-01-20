from django.test import TestCase
from django.contrib.auth import get_user_model

from acoes.models import Acao, Carteira, Movimentacao

User = get_user_model()


class AcaoTestCase(TestCase):

    def setUp(self):
        self.acao = Acao.objects.create(
            ticker='ACAO3',
            preco=123.45,
        )

    def tearDown(self):
        Acao.objects.all().delete()

    def test_create_acao(self):
        """ Criar ação """
        Acao.objects.create(
            ticker='ACAO4',
            preco=4.50,
        )
        self.assertEqual(Acao.objects.count(), 2)

    def test_update_acao(self): 
        """ Atualizar uma ação """  
        self.acao.ticker = 'NOVO3'
        self.acao.preco = 23.83
        self.acao.save()
        self.assertEqual(self.acao.ticker, 'NOVO3')
        self.assertEqual(self.acao.preco, 23.83)
        
    def test_delete_acao(self):
        """ Deletar uma ação """
        self.acao.delete()
        self.assertEqual(Acao.objects.count(), 0)


class MovimentacaoTestCase(TestCase):

    def setUp(self):
        self.acao = Acao.objects.create(
            ticker='ACAO3',
            preco=10.50,
        )
        self.user = User.objects.create_user(
            email='teste@teste.com',
            password='minha_senha'
        )

    def tearDown(self):
        Movimentacao.objects.all().delete()

    def test_create_movimentacao(self):
        """ Criar movimentacao """
        movimentacao = Movimentacao.objects.create(
            acao=self.acao,
            data_movimentacao='2022-01-17',
            tipo='V',
            preco=4.50,
            preco_medio_venda=4.75,
            quantidade=100,
            valor_total=450.00,
            user=self.user
        )
        self.assertEqual(movimentacao.acao, self.acao)
        self.assertEqual(movimentacao.data_movimentacao, '2022-01-17')
        self.assertEqual(movimentacao.tipo, 'V')
        self.assertEqual(movimentacao.preco, 4.50)
        self.assertEqual(movimentacao.preco_medio_venda, 4.75)
        self.assertEqual(movimentacao.quantidade, 100)
        self.assertEqual(movimentacao.valor_total, 450.00)
        self.assertEqual(movimentacao.user, self.user)
        self.assertEqual(Movimentacao.objects.count(), 1)
    

class CarteiraTestCase(TestCase):

    def setUp(self):
        self.acao = Acao.objects.create(
            ticker='ACAO3',
            preco=10.50,
        )
        self.user = User.objects.create_user(
            email='teste@teste.com',
            password='minha_senha'
        )
        self.carteira = Carteira.objects.create(
            user=self.user,
            acao=self.acao,
            valor_investido=1050.00,
            preco_medio=10.50,
            quantidade=100
        )
        self.user_2 = User.objects.create_user(
            email='teste2@teste.com',
            password='minha_senha'
        )

    def tearDown(self):
        Carteira.objects.all().delete()

    def test_create_carteira(self):
        """ Criar carteira """
        Carteira.objects.create(
            user=self.user_2,
            acao=self.acao,
            valor_investido=500.00,
            preco_medio=50.00,
            quantidade=100
        )
        self.assertEqual(Carteira.objects.count(), 2)

    def test_update_carteira(self): 
        """ Atualizar carteira """
        self.carteira.valor_investido = 3000.00
        self.carteira.preco_medio = 3.00
        self.carteira.quantidade = 1000
        self.assertEqual(self.carteira.valor_investido, 3000.00)
        self.assertEqual(self.carteira.preco_medio, 3.00)
        self.assertEqual(self.carteira.quantidade, 1000.00)
        
    def test_delete_carteira(self):
        """ Deletar carteira """
        self.carteira.delete()
        self.assertEqual(Carteira.objects.count(), 0)
