from django.urls import path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'get_messages', views.UserMessageViewSet, basename='getUserMessages')
# router.register(r'send', views.MessageViewSet)
urlpatterns = router.urls
