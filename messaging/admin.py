from django.contrib import admin
from .models import Message, UserMessage


# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")


admin.site.register(Message, ProfileAdmin)
admin.site.register(UserMessage, ProfileAdmin)

