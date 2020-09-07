from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserLog(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_id')
    action_time = models.DateField(auto_now_add=True)
    action = models.CharField(max_length=20, verbose_name='action_name')
    meta = models.CharField(max_length=150)

    def __str__(self):
        return self.action
