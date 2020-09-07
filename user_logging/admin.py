from django.contrib import admin
from user_logging.models import UserLog


# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ("action_time",)


admin.site.register(UserLog, ProfileAdmin)
