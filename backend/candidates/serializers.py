from rest_framework import serializers

from .models import Candidate


class CandidateSerializer(serializers.ModelSerializer):
    case_id = serializers.SerializerMethodField()
    def get_case_id(self, obj):
        case = getattr(obj, 'bgv_case', None)

        if case:
            return case.id

        return None

    class Meta:
        model = Candidate
        fields = [
            'id',
            'user',
            'client',
            'candidate_code',
            'first_name',
            'last_name',
            'email',
            'phone',
            'date_of_birth',
            'address',
            'city',
            'state',
            'pincode',
            'status',
            'created_by',
            'created_at',
            'updated_at',
            'case_id',
        ]

        read_only_fields = [
            'id',
            'candidate_code',
            'created_by',
            'created_at',
            'updated_at',
        ]

class CandidateClientAssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = [
            'client',
        ]

    def validate_client(self, value):
        if value.role != 'CLIENT':
            raise serializers.ValidationError(
                'Only CLIENT users can be assigned.'
            )

        if not value.is_active:
            raise serializers.ValidationError(
                'Selected client is inactive.'
            )

        return value