from django.db import models
from django.contrib.auth.models import User


class UserBlacklist(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='current_user')
    blockedId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_user')
    created_at = models.DateTimeField(auto_now_add=True)
