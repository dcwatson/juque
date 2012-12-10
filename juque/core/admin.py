from django.contrib import admin
from juque.core.models import User

class UserAdmin (admin.ModelAdmin):
    list_display = ('name', 'email', 'storage_backend', 'aws_bucket')
    ordering = ('name',)

admin.site.register(User, UserAdmin)
