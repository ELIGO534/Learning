

# Register your models here.
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'password')  # Display name in admin list view
    search_fields = ('name', 'phone')  # Allow searching by name and phone
    ordering = ('id',)
