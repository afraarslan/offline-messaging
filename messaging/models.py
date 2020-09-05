from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Message(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.content


class UserMessage(models.Model):
    messageId = models.ForeignKey(Message, on_delete=models.CASCADE)
    fromId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    toId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')
    # content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
