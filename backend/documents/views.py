from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsAdminOrHR, IsVerifier, IsCandidate, IsClient
from rest_framework.filters import SearchFilter
from .models import Document
from .serializers import DocumentSerializer, DocumentVerificationSerializer
from rest_framework.exceptions import PermissionDenied

from audit_logs.models import AuditLog
from audit_logs.utils import create_audit_log


class DocumentCreateView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAdminOrHR]

    def perform_create(self, serializer):
        document = serializer.save(
            uploaded_by=self.request.user
        )

        case = getattr(
            document.candidate,
            'bgv_case',
            None
        )

        if not case:
            return

        create_audit_log(
            user=self.request.user,
            case=case,
            action=AuditLog.Action.DOCUMENT_UPLOADED,
            description=(
                f'{document.document_name} was uploaded for '
                f'{case.case_number}.'
            )
        )

class DocumentListView(generics.ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAdminOrHR]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
    ]
    filterset_fields = [
        'candidate',
        'verification',
        'document_type',
        'status',
        'uploaded_by',
    ]

    search_fields = [
        'document_name',
        'document_type',
        'status',
    ]


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAdminOrHR]


class DocumentVerificationView(generics.UpdateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentVerificationSerializer
    permission_classes = [IsVerifier]

    def get_object(self):
        document = super().get_object()

        if document.verification is None:
            raise PermissionDenied(
                "This document is not linked to a verification."
            )
        if document.verification.assigned_to != self.request.user:
            raise PermissionDenied(
                "You can only verify documents linked to verifications assigned to you."
            )
        return document

    def perform_update(self, serializer):
        document = serializer.save()

        verification = document.verification
        case = verification.candidate.bgv_case

        create_audit_log(
            user=self.request.user,
            case=case,
            action=AuditLog.Action.    DOCUMENT_VERIFIED,
            description=(
                f'{document.document_name} for '
                f'{case.case_number} was updated     to '
                f'{document.status}.'
            )
        )

class MyDocumentListView(generics.ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsVerifier]

    def get_queryset(self):
        return Document.objects.filter(
            verification__assigned_to=self.request.user
        )

class CandidateDocumentListView(generics.ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsCandidate]

    def get_queryset(self):
        return Document.objects.filter(
            candidate__user=self.request.user
        )

class ClientDocumentListView(generics.ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return Document.objects.filter(
            candidate__client=self.request.user
        )