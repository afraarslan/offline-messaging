from django.test import TestCase, Client
from .models import UserBlacklist, User
from django.urls import reverse, resolve
from .views import registration, login, block_a_user
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, APIClient, force_authenticate

factory = APIRequestFactory()
request = factory.post('/register/',
                       {'username': 'example_arif', 'password': 'example'},
                       content_type='application/json')


# Create your tests here.

class TestUrls(TestCase):
    def test_register_url(self):
        url = reverse('register')
        self.assertEquals(resolve(url).func, registration)

    def test_login_url(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, login)

    def test_block_url(self):
        url = reverse('block')
        self.assertEquals(resolve(url).func, block_a_user)


class TestViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.block_user_url = reverse('block')
        self.factory = APIRequestFactory()
        self.example_user = User.objects.create(username="example_arif", password="example")

    def test_registration_already_exists(self):
        request = self.factory.post(self.register_url)
        force_authenticate(request, user=self.example_user)
        response = registration(request)
        self.assertEquals(response.status_code, 400)

        # response = self.client.post(self.register_url, self.example_user)
        # self.assertTemplateUsed(response, 'search/search.html')

    def test_registration_mismatch_password(self):
        response = self.client.post(self.register_url, {
            'username': "example_ahmet",
            'password': "example",
            'password2': "exampl"
        }, format='json')

        self.assertEqual(response.resolver_match.func, registration)
        self.assertEquals(response.status_code, 400)
        # self.assertTemplateUsed(response, 'search/search.html')

    def test_registration_post(self):
        response = self.client.post(self.register_url, {
            'username': "example_ahmet",
            'password': "example",
            'password2': "example"
        }, format='json')

        self.assertEqual(response.resolver_match.func, registration)
        self.assertEquals(response.status_code, 201)
        # self.assertTemplateUsed(response, 'search/search.html')


    # def test_block_user_post(self):
    #     response = self.client.post(self.block_user_url, {})
    #
    #     self.assertEqual(response.resolver_match.func, block_a_user)
    #     self.assertEquals(response.status_code, 200)
    #     # self.assertTemplateUsed(response, 'search/search.html')
