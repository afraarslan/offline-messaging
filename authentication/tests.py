from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserBlacklist, User
from django.urls import reverse, resolve
from .views import registration, login, block_a_user
from rest_framework import status
from rest_framework.test import APIClient


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


class TestRegisterViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.example_user = User(username='example_arif')
        self.example_user.set_password('pass')
        self.example_user.save()

    def test_with_no_data(self):
        resp = self.client.post(self.register_url, {}, format='json')

        self.assertEqual(resp.data, {
            "username": [
                "This field is required."
            ],
            "password": [
                "This field is required."
            ],
            "password2": [
                "This field is required."
            ]
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_no_username(self):
        resp = self.client.post(self.register_url, {
            'password': 'pass',
            'password2': 'pass'
        }, format='json')

        self.assertEqual(resp.data, {
            "username": [
                "This field is required."
            ]
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_no_password(self):
        resp = self.client.post(self.register_url, {
            'username': 'example_kamil',
        }, format='json')

        self.assertEqual(resp.data, {
            "password": [
                "This field is required."
            ],
            "password2": [
                "This field is required."
            ]
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_already_exists(self):
        resp = self.client.post(self.register_url, {
            'username': 'example_arif',
            'password': 'pass',
            'password2': 'pass'
        }, format='json')

        self.assertEqual(resp.data, {
            "username": [
                "A user with that username already exists."
            ]
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_passwords_mismatch(self):
        resp = self.client.post(self.register_url, {
            'username': 'example_kamil',
            'password': 'pass',
            'password2': 'pass2'
        }, format='json')

        self.assertEqual(resp.data, {
            "password": "Passwords should be same."
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_correct_registration(self):
        resp = self.client.post(self.register_url, {
            'username': 'example_kamil',
            'password': 'pass',
            'password2': 'pass'
        }, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(len(resp.data), 3)
        self.assertEqual(resp.data['user']['username'], "example_kamil")
        self.assertTrue('access', 'refresh' in resp.data)


class TestLoginViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')

        self.example_user = User(username='example_arif')
        self.example_user.set_password('pass')
        self.example_user.save()

    def test_login_with_no_data(self):
        resp = self.client.post(self.login_url, {}, format='json')

        self.assertEqual(resp.data, {
            "username": [
                "This field may not be null."
            ],
            "password": [
                "This field may not be null."
            ]
        })

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_wrong_username(self):
        resp = self.client.post(self.login_url, {
            'username': 'wrong',
            'password': 'pass'
        }, format='multipart')

        self.assertEqual(resp.data, {
            "user": "username or password is invalid"
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_wrong_password(self):
        resp = self.client.post(self.login_url, {
            'username': 'example_arif',
            'password': 'wrong'
        }, format='json')

        self.assertEqual(resp.data, {
            "user": "username or password is invalid"
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_correct_credentials(self):
        resp = self.client.post(self.login_url, {
            'username': "example_arif",
            'password': "pass"
        }, format='json')
        print(resp.data)
        self.assertEqual(len(resp.data), 3)
        self.assertEqual(resp.data['user']['username'], "example_arif")
        self.assertTrue('access', 'refresh' in resp.data)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class TestBlockUserViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.block_user_url = reverse('block')

        self.example_user1 = User(username='example_arif')
        self.example_user1.set_password('pass')
        self.example_user1.save()

        self.example_user2 = User(username='example_kamil')
        self.example_user2.set_password('pass')
        self.example_user2.save()

        self.response = self.client.post('/api/authentication/token/', {
            'username': "example_arif",
            'password': "pass"
        }, format='json')
        self.access_token = self.response.data['access']

    def test_block_a_user_with_no_data(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        resp = self.client.post(self.block_user_url, {}, format='json')

        self.assertEqual(resp.data, {
            "blocked_id": [
                "This field is required."
            ]
        })

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_block_a_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        print('ok')
        resp = self.client.post(self.block_user_url, {
            'blocked_id': self.example_user2.pk
        }, format='json')
        print('done')
        self.assertEqual(resp.data, 'blocked_instance')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_block_non_existed_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        resp = self.client.post(self.block_user_url, {
            'blocked_id': 10000
        }, format='json')

        self.assertEqual(resp.data, {
            "blocked_id": [
                "not exists"
            ]
        })

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_block_already_blocked_user(self):
        blocked_instance = UserBlacklist(
            user=self.example_user1,
            blocked_user=self.example_user2
        )
        blocked_instance.save()

        print('done')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        resp = self.client.post(self.block_user_url, {
            'blocked_id': self.example_user2.pk
        }, format='json')

        print('blocked_id')
        self.assertEqual(resp.data, {
            "blocked_id": "already blocked"
        })

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
