from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        'username',
        'email',
        'role',
        'phone',
        'is_active',
        'is_staff',
    )

    list_filter = (
        'role',
        'is_active',
        'is_staff',
    )

    search_fields = (
        'username',
        'email',
        'phone',
    )

    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        (
            'BGV Information',
            {
                'fields': (
                    'role',
                    'phone',
                )
            }
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'BGV Information',
            {
                'fields': (
                    'email',
                    'role',
                    'phone',
                )
            }
        ),
    )