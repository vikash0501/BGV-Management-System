from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'case',
        'action',
        'created_at',
    )

    list_filter = (
        'action',
        'created_at',
    )

    search_fields = (
        'user__username',
        'case__case_number',
        'description',
    )

    readonly_fields = (
        'created_at',
    )

    ordering = (
        '-created_at',
    )