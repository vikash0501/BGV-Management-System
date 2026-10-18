from rest_framework import serializers
from verifications.models import Verification
from .models import BGVCase


class BGVCaseSerializer(serializers.ModelSerializer):
    candidate_name = serializers.SerializerMethodField()
    candidate_code = serializers.CharField(
        source='candidate.candidate_code',
        read_only=True
    )
    assigned_to_username = serializers.CharField(
        source='assigned_to.username',
        read_only=True
    )
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    report_id = serializers.SerializerMethodField()
    report_status = serializers.SerializerMethodField()

    class Meta:
        model = BGVCase
        fields = [
            'id',
            'case_number',
            'candidate',
            'candidate_name',
            'candidate_code',
            'status',
            'assigned_to',
            'assigned_to_username',
            'priority',
            'remarks',
            'created_by',
            'created_by_username',
            'report_id',
            'report_status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'created_by_username',
            'candidate_name',
            'candidate_code',
            'assigned_to_username',
            'created_at',
            'updated_at',
        ]

    def get_candidate_name(self, obj):
        return f"{obj.candidate.first_name} {obj.candidate.last_name}".strip()

    def validate_case_number(self, value):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "Case number cannot be empty."
            )

        return value

    def validate_candidate(self, value):
        if BGVCase.objects.filter(candidate=value).exists():
            raise serializers.ValidationError(
                "A BGV case already exists for this candidate."
            )

        return value
    def get_report_id(self, obj):
        report = getattr(obj.candidate, 'report', None)

        if not report:
            return None

        return report.id


    def get_report_status(self, obj):
        report = getattr(obj.candidate, 'report', None)

        if not report:
            return None

        return report.status

class BGVCaseAssignmentSerializer(serializers.Serializer):
    assigned_to = serializers.IntegerField()

    def validate_assigned_to(self, value):
        from accounts.models import User

        try:
            user = User.objects.get(
                id=value,
                role=User.Role.VERIFIER,
                is_active=True
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Selected user must be an active VERIFIER."
            )

        return user

class BGVCaseProcessingSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            BGVCase.Status.IN_PROGRESS,
            BGVCase.Status.COMPLETED,
            BGVCase.Status.ON_HOLD,
            BGVCase.Status.CLOSED,
        ]
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True
    )

class CreateCaseVerificationsSerializer(serializers.Serializer):
    verification_types = serializers.ListField(
        child=serializers.ChoiceField(
            choices=Verification.VerificationType.choices
        ),
        required=False
    )

class CaseStatusSyncSerializer(serializers.Serializer):
    pass