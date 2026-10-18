from django.utils import timezone
from verifications.models import Verification
from rest_framework import generics, status
from rest_framework.response import Response
from accounts.permissions import IsAdminOrHR, IsClient

from .models import Report
from .serializers import (ReportSerializer, ClientReportSerializer, ClientReportDetailSerializer, ReportVerificationSerializer,
StructuredReportSerializer,
)

from audit_logs.models import AuditLog
from audit_logs.utils import create_audit_log

class ReportCreateView(generics.CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAdminOrHR]

    def perform_create(self, serializer):
        status_value = serializer.validated_data.get('status')

        if status_value == Report.Status.FINAL:
            serializer.save(
                generated_at=timezone.now()
            )
        else:
            serializer.save()


class ClientFinalReportListView(generics.ListAPIView):
    serializer_class = ClientReportSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return Report.objects.filter(
            candidate__client=self.request.user,
            status=Report.Status.FINAL
        )

class ClientReportDetailView(generics.RetrieveAPIView):
    serializer_class = ClientReportDetailSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return Report.objects.filter(
            candidate__client=self.request.user,
            status=Report.Status.FINAL
        )

class ClientReportVerificationView(generics.ListAPIView):
    serializer_class = ReportVerificationSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return Verification.objects.filter(
            candidate__client=self.request.user,
            candidate__final_report__status=Report.Status.FINAL,
            candidate_id=self.kwargs['candidate_id']
        )

class ReportGenerateView(generics.GenericAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAdminOrHR]

    def post(self, request, pk):
        report = self.get_object()

        required_types = {
            Verification.VerificationType.EMPLOYMENT,
            Verification.VerificationType.EDUCATION,
            Verification.VerificationType.ADDRESS,
            Verification.VerificationType.IDENTITY,
        }

        verifications = Verification.objects.filter(
            candidate=report.candidate
        )

        verified_types = set(
            verifications.filter(
                status=Verification.Status.VERIFIED
            ).values_list(
                'verification_type',
                flat=True
            )
        )

        missing_types = required_types - verified_types

        if missing_types:
            return Response(
                {
                    "detail": "Report cannot be generated.",
                    "missing_verifications": list(missing_types)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        candidate = report.candidate

        summary_lines = [
            "BGV Report Generated Successfully.",
            "",
            f"Candidate: {candidate.first_name} {candidate.last_name}",
            f"Candidate Code: {candidate.candidate_code}",
            "",
            "Verification Results:"
        ]

        for verification in verifications:
            summary_lines.append(
                f"- {verification.verification_type}: "
                f"{verification.status}"
            )

            if verification.remarks:
                summary_lines.append(
                    f"  Remarks: {verification.remarks}"
                )

            if verification.result:
                summary_lines.append(
                    f"  Result: {verification.result}"
                )

        summary_lines.append("")
        summary_lines.append("Overall BGV Status: VERIFIED")

        report.summary = "\n".join(summary_lines)
        report.status = Report.Status.FINAL
        report.generated_at = timezone.now()

        report.save(
            update_fields=[
                'summary',
                'status',
                'generated_at',
                'updated_at',
            ]
        )
        create_audit_log(
            user=request.user,
            case=report.candidate.bgv_case,
            action=AuditLog.Action.REPORT_GENERATED,
            description=(
                f'BGV report for '
                f'{report.candidate.bgv_case.case_number} '
                f'was generated successfully.'
            )
        )

        return Response(
            ReportSerializer(report).data,
            status=status.HTTP_200_OK
        )

class ClientStructuredReportView(generics.RetrieveAPIView):
    serializer_class = StructuredReportSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return Report.objects.filter(
            candidate__client=self.request.user,
            status=Report.Status.FINAL
        )