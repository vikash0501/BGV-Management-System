from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Verification
from cases.models import BGVCase
from rest_framework.filters import SearchFilter
from accounts.permissions import IsAdminOrHR, IsVerifier, IsClient
from rest_framework.exceptions import PermissionDenied
from .models import Verification
from .serializers import (
    VerificationSerializer,
    VerificationAssignmentSerializer,
    VerificationProcessSerializer,
)

from audit_logs.models import AuditLog
from audit_logs.utils import create_audit_log

class VerificationCreateView(generics.CreateAPIView):
    queryset = Verification.objects.all()
    serializer_class = VerificationSerializer
    permission_classes = [IsAdminOrHR]

    def perform_create(self, serializer):
        verification = serializer.save()

        case = getattr(
            verification.candidate,
            'bgv_case',
            None
        )

        if not case:
            return

        create_audit_log(
            user=self.request.user,
            case=case,
            action=AuditLog.Action.VERIFICATION_CREATED,
            description=(
                f'{verification.verification_type} verification '
                f'was created for '
                f'{case.case_number}.'
            )
        )

class VerificationListView(generics.ListAPIView):
    queryset = Verification.objects.all()
    serializer_class = VerificationSerializer
    permission_classes = [IsAdminOrHR]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
    ]

    filterset_fields = [
        'candidate',
        'verification_type',
        'status',
        'assigned_to',
    ]

    search_fields = [
        'verification_type',
        'status',
        'remarks',
        'result',
    ]

class VerificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Verification.objects.all()
    serializer_class = VerificationSerializer
    permission_classes = [IsAdminOrHR]

class VerificationAssignmentView(generics.UpdateAPIView):
    queryset = Verification.objects.all()
    serializer_class = VerificationAssignmentSerializer
    permission_classes = [IsAdminOrHR]

    def perform_update(self, serializer):
        verification = serializer.save()

        create_audit_log(
            user=self.request.user,
            case=verification.candidate.bgv_case,
            action=AuditLog.Action.VERIFICATION_ASSIGNED,
            description=(
                f'{verification.verification_type} verification '
                f'for {verification.candidate.bgv_case.case_number} '
                f'was assigned to '
                f'{verification.assigned_to.username}.'
            )
        )

class MyVerificationListView(generics.ListAPIView):
    serializer_class = VerificationSerializer
    permission_classes = [IsVerifier]

    def get_queryset(self):
        return Verification.objects.filter(
            assigned_to=self.request.user
        )

class VerificationProcessView(generics.UpdateAPIView):
    queryset = Verification.objects.all()
    serializer_class = VerificationProcessSerializer
    permission_classes = [IsVerifier]

    def get_object(self):
        verification = super().get_object()

        if verification.assigned_to != self.request.user:
            raise PermissionDenied(
                "You can only process verifications assigned to you."
            )

        return verification

    def perform_update(self, serializer):
        verification = serializer.save()

        case = getattr(
            verification.candidate,
            'bgv_case',
            None
        )

        if not case:
            return

        verifications = verification.candidate.verifications.all()

        total = verifications.count()

        verified = verifications.filter(
            status=Verification.Status.VERIFIED
        ).count()

        in_progress = verifications.filter(
            status=Verification.Status.IN_PROGRESS
        ).count()

        failed = verifications.filter(
            status=Verification.Status.FAILED
        ).count()

        on_hold = verifications.filter(
            status=Verification.Status.ON_HOLD
        ).count()

        if total == 0:
            new_case_status = BGVCase.Status.OPEN

        elif verified == total:
            new_case_status = BGVCase.Status.COMPLETED

        elif failed > 0 or on_hold > 0:
            new_case_status = BGVCase.Status.ON_HOLD

        elif in_progress > 0:
            new_case_status = BGVCase.Status.IN_PROGRESS

        else:
            new_case_status = BGVCase.Status.OPEN

        case.status = new_case_status

        case.save(
            update_fields=[
                'status',
                'updated_at',
            ]
        )

        create_audit_log(
            user=self.request.user,
            case=case,
            action=AuditLog.Action.VERIFICATION_PROCESSED,
            description=(
                f'{verification.verification_type} verification '
                f'for {case.case_number} was updated to '
                f'{verification.status}.'
            )
        )

class ClientVerificationListView(generics.ListAPIView):
    serializer_class = VerificationSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return Verification.objects.filter(
            candidate__client=self.request.user
        )