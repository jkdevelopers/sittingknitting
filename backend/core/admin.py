from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib import admin
from .models import *


class UserAdmin(AuthUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'phone']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']

    fieldsets = [
        [None, {
            'fields': [
                'email',
                'password',
            ]
        }],
        ['Персональные данные', {
            'fields': [
                'first_name',
                'last_name',
                'phone',
                'address'
            ]
        }],
        ['Метки и разрешения', {
            'fields': [
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ]
        }],
        ['Важные даты', {
            'fields': [
                'last_login',
                'date_joined',
            ]
        }],
    ]

    add_fieldsets = [
        [None, {
            'classes': ['wide'],
            'fields': [
                'email',
                'password1',
                'password2',
            ],
        }],
    ]


admin.site.register(Component)
admin.site.register(User, UserAdmin)
