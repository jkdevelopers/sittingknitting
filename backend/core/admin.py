from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib import admin
from .models import *


class UserAdmin(AuthUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'phone']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']

    fieldsets = [
        ['Персональные данные', {'fields': ['email', 'first_name', 'last_name', 'phone', 'address']}],
        ['Метки и разрешения', {'fields': ['is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions']}],
        ['Важные даты', {'fields': ['last_login', 'date_joined']}],
        ['Безопасность', {'fields': ['password']}]
    ]

    add_fieldsets = [
        [None, {'fields': ['email', 'password1', 'password2'], 'classes': ['wide']}],
    ]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']
    ordering = ['name']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'name', 'price', 'quantity', 'active']
    list_filter = ['category', 'active']
    search_fields = ['name', 'brand', 'vendor']
    ordering = ['vendor']


admin.site.register(User, UserAdmin)
admin.site.register(Component)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
