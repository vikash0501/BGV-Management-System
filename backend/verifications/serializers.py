from rest_framework import serializers

from .models import Verification


class VerificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Verification

        fields = [
            'id',
            'candidate',
            'verification_type',
            'status',
            'assigned_to',
            'remarks',
            'result',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]

class VerificationAssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Verification
        fields = [
            'assigned_to',
        ]

    def validate_assigned_to(self, value):
        if value.role != 'VERIFIER':
            raise serializers.ValidationError(
                'Only VERIFIER users can be assigned.'
            )

        if not value.is_active:
            raise serializers.ValidationError(
                'Selected verifier is inactive.'
            )

        return value


class VerificationProcessSerializer(serializers.ModelSerializer):

    class Meta:
        model = Verification
        fields = [
            'status',
            'remarks',
            'result',
        ]

    def validate_status(self, value):
        allowed_statuses = [
            'IN_PROGRESS',
            'VERIFIED',
            'FAILED',
            'ON_HOLD',
        ]

        if value not in allowed_statuses:
            raise serializers.ValidationError(
                'Invalid verification status.'
            )

        return value