from django.contrib import admin

from jwtauth.models import UserBlacklist
from .models import Message, UserMessage


# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")


admin.site.register(Message, ProfileAdmin)
admin.site.register(UserMessage)
admin.site.register(UserBlacklist)


