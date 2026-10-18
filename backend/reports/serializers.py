from rest_framework import serializers
from verifications.models import Verification
from .models import Report


class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Report
        fields = [
            'id',
            'candidate',
            'status',
            'summary',
            'generated_at',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'generated_at',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):
        status_value = attrs.get('status')
        if status_value == Report.Status.FINAL:
            candidate = attrs.get('candidate')
            required_types = {
                Verification.VerificationType.EMPLOYMENT,
                Verification.VerificationType.EDUCATION,
                Verification.VerificationType.ADDRESS,
                Verification.VerificationType.IDENTITY,
            }
            verified_types = set(
                Verification.objects.filter(
                    candidate=candidate,
                    status=Verification.Status.VERIFIED
                ).values_list(
                    'verification_type',
                    flat=True
                )
            )
            missing_types = required_types - verified_types

            if missing_types:
                raise serializers.ValidationError({
                    'status' : (
                        'Report cannot be marked FINAL. '
                        'All required verifications must be VERIFIED.'
                    ),
                    'missing_verifications':list(missing_types),
                })
        return attrs

class ClientReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Report
        fields = [
            'id',
            'candidate',
            'status',
            'summary',
            'generated_at',
        ]

class ClientReportDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Report
        fields = [
            'id',
            'candidate',
            'status',
            'summary',
            'generated_at',
            'created_at',
            'updated_at',
        ]

class ReportVerificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Verification
        fields = [
            'id',
            'verification_type',
            'status',
            'remarks',
            'result',
            'assigned_to',
            'created_at',
            'updated_at',
        ]

class StructuredReportSerializer(serializers.ModelSerializer):
    candidate_name = serializers.SerializerMethodField()
    candidate_code = serializers.CharField(
        source='candidate.candidate_code',
        read_only=True
    )
    verifications = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id',
            'candidate',
            'candidate_name',
            'candidate_code',
            'status',
            'summary',
            'generated_at',
            'verifications',
        ]

    def get_candidate_name(self, obj):
        return (
            f"{obj.candidate.first_name} "
            f"{obj.candidate.last_name}"
        )

    def get_verifications(self, obj):
        from verifications.models import Verification

        verifications = Verification.objects.filter(
            candidate=obj.candidate
        )

        return [
            {
                'id': verification.id,
                'type': verification.verification_type,
                'status': verification.status,
                'remarks': verification.remarks,
                'result': verification.result,
                'assigned_to': verification.assigned_to_id,
            }
            for verification in verifications
        ]