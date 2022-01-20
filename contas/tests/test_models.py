from django.test import TestCase
from django.contrib.auth import get_user_model


User = get_user_model()


class UserTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='meuemail@email.com',
            first_name="Primeiro Nome",
            last_name="Sobrenome",
            password='minhasenhasecreta'
        )

    def tearDown(self):
        User.objects.all().delete()

    def test_create_user(self):
        """ Criar um usuário """
        User.objects.create_user(
            email='meuemail2@email.com',
            first_name="Primeiro Nome2",
            last_name="Sobrenome2",
            password='minhasenhasecreta'
        )
        self.assertEqual(User.objects.count(), 2)

    def test_update_user(self): 
        """ Atualizar um usuário """  
        self.user.first_name = 'Novo primeiro nome'
        self.user.email = 'novo@email.com'
        self.user.save()
        self.assertEqual(self.user.first_name, 'Novo primeiro nome')
        self.assertEqual(self.user.email, 'novo@email.com')
        
    def test_delete_user(self):
        """ Deletar um usuário """
        self.user.delete()
        self.assertEqual(User.objects.count(), 0)