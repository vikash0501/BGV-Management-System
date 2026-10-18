from django.contrib import admin

from .models import BGVCase


@admin.register(BGVCase)
class BGVCaseAdmin(admin.ModelAdmin):
    list_display = (
        'case_number',
        'candidate',
        'status',
        'assigned_to',
        'priority',
        'created_by',
        'created_at',
    )

    list_filter = (
        'status',
        'priority',
        'created_at',
    )

    search_fields = (
        'case_number',
        'candidate__candidate_code',
        'candidate__first_name',
        'candidate__last_name',
        'candidate__email',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )