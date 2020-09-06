from django.urls import path
from rest_framework import routers
from . import views

urlpatterns = [
    path('get-inbox/', views.get_inbox_messages, name='get_inbox'),
    path('get-outbox/', views.get_sent_messages, name='get_outbox'),
    path('send/', views.send_message, name='send'),
]