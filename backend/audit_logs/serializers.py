from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    case_number = serializers.CharField(
        source='case.case_number',
        read_only=True
    )

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'username',
            'case',
            'case_number',
            'action',
            'description',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'user',
            'username',
            'case_number',
            'created_at',
        ]