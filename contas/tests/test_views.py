from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from django.contrib.auth import get_user_model


User = get_user_model()

class LoginViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            email='teste@teste.com',
            password='123'
        )

    def tearDown(self):
        self.user.delete()

    def test_login_ok(self):
        """ Teste de login com credenciais corretas """
        response = self.client.get(self.login_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'contas/login.html')
        data = {'email': self.user.email, 'password': '123'}
        response = self.client.post(self.login_url, data)
        redirect_url = reverse(settings.LOGIN_REDIRECT_URL)
        self.assertRedirects(response, redirect_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_error(self):
        """ Teste de login com credenciais incorretas """
        data = {'email': self.user.email, 'password': '1234'}
        response = self.client.post(self.login_url, data)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'contas/login.html')