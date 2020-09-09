from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve

from authentication.models import UserBlacklist
from user_logging.models import UserLog
from .models import Message, UserMessage
from .serializers import UserMessageSerializer
from .views import get_outbox_messages, get_inbox_messages, send_message
from rest_framework import status
from rest_framework.test import APIClient


class TestUrls(TestCase):
    def test_register_url(self):
        url = reverse('get_inbox')
        self.assertEquals(resolve(url).func, get_inbox_messages)

    def test_login_url(self):
        url = reverse('get_outbox')
        self.assertEquals(resolve(url).func, get_outbox_messages, )

    def test_block_url(self):
        url = reverse('send')
        self.assertEquals(resolve(url).func, send_message)


class TestGetInboxViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.get_inbox_url = reverse('get_inbox')

        self.example_user = User(username='example_arif')
        self.example_user.set_password('pass')
        self.example_user.save()

        self.response = self.client.post('/api/authentication/token/', {
            'username': "example_arif",
            'password': "pass"
        }, format='multipart')

        self.refresh = self.response.data['refresh']
        self.access = self.response.data['access']

    def test_get_inbox_before_have_message(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access)
        resp = self.client.get(self.get_inbox_url, {}, format='multipart')
        self.assertEqual(resp.data, [])
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_get_inbox_when_have_message(self):
        text = "it is a new message."
        newMessage = Message(content=text)
        newMessage.save()

        userMessage = UserMessage(from_user=self.example_user,
                                  to_user=self.example_user,
                                  message=newMessage)
        userMessage.save()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access)
        resp = self.client.get(self.get_inbox_url, {}, format='multipart')

        self.assertEqual(resp.data[0]['message']['content'], text)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class TestGetOutboxViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.get_outbox_url = reverse('get_outbox')

        self.example_user = User(username='example_arif')
        self.example_user.set_password('pass')
        self.example_user.save()
        self.response = self.client.post('/api/authentication/token/', {
            'username': "example_arif",
            'password': "pass"
        }, format='multipart')

        self.refresh = self.response.data['refresh']
        self.access = self.response.data['access']

    def test_get_outbox_before_have_message(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access)
        resp = self.client.get(self.get_outbox_url, {}, format='multipart')

        self.assertEqual(resp.data, [])
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_get_outbox_when_have_message(self):
        text = "it is a new message."
        newMessage = Message(content=text)
        newMessage.save()

        userMessage = UserMessage(from_user=self.example_user,
                                  to_user=self.example_user,
                                  message=newMessage)
        userMessage.save()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access)
        resp = self.client.get(self.get_outbox_url, {}, format='multipart')

        self.assertEqual(resp.data[0]['message']['content'], text)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class TestSendMessageViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.send_url = reverse('send')

        self.example_user1 = User(username='example_arif')
        self.example_user1.set_password('pass')
        self.example_user1.save()

        self.response = self.client.post('/api/authentication/token/', {
            'username': "example_arif",
            'password': "pass"
        }, format='multipart')
        self.refresh = self.response.data['refresh']
        self.access = self.response.data['access']

        self.example_user2 = User(username='example_kamil')
        self.example_user2.set_password('pass')
        self.example_user2.save()
        UserLog.objects.all().delete()

    def test_send_message_with_no_to_user_id(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access)
        resp = self.client.post(self.send_url, {
            'text': 'hey'
        }, format='multipart')

        self.assertEqual(resp.data, {
            "to_user_id": [
                "This field is required."
            ]
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_message_with_no_text(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access)
        resp = self.client.post(self.send_url, {
            'to_user_id': 2
        }, format='multipart')

        self.assertEqual(resp.data, {
            "text": [
                "This field is required."
            ]
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_message_to_non_exists_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access)
        resp = self.client.post(self.send_url, {
            'to_user_id': 10000,
            'text': 'is there anyone?'
        }, format='multipart')

        self.assertEqual(resp.data, {
            "to_user_id": [
                "User should be exist."
            ]
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_message(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access)
        resp = self.client.post(self.send_url, {
            'to_user_id': self.example_user2.pk,
            'text': 'hello'
        }, format='multipart')

        self.assertEqual(resp.data, {'success'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_send_message_after_user_blocked(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access)

        blocked_instance = UserBlacklist(user=self.example_user2, blocked_user=self.example_user1)
        blocked_instance.save()

        resp = self.client.post(self.send_url, {
            'to_user_id': self.example_user2.pk,
            'text': 'is there anyone?'
        }, format='multipart')

        self.assertEqual(resp.data, {
            "to_user_id": [
                "You are blocked. You cannot send a message."
            ]
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_logs_after_send_message(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access)
        resp = self.client.post(self.send_url, {
            'to_user_id': self.example_user2.pk,
            'text': 'hello'
        }, format='multipart')

        user_log = UserLog.objects.first()

        self.assertEqual(user_log.action, 'send')
        self.assertEqual(user_log.user.id, self.example_user1.pk)
        self.assertEqual(resp.data, {'success'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
