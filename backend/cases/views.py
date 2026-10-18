
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from verifications.models import Verification
from accounts.permissions import IsAdminOrHR, IsVerifier, IsClient, IsCandidate
from django.utils import timezone
from datetime import timedelta
from .models import BGVCase
from reports.models import Report
from documents.models import Document
from .serializers import BGVCaseSerializer, BGVCaseAssignmentSerializer, BGVCaseProcessingSerializer, CreateCaseVerificationsSerializer
from io import BytesIO
from django.http import FileResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from audit_logs.models import AuditLog
from audit_logs.utils import create_audit_log



class BGVCaseListCreateView(APIView):
    permission_classes = [IsAdminOrHR]

    def get(self, request):
        cases = (
            BGVCase.objects
            .select_related(
                'candidate',
                'assigned_to',
                'created_by',
            )
            .all()
            .order_by('-created_at')
        )

        status_value = request.query_params.get('status')
        priority = request.query_params.get('priority')
        candidate_id = request.query_params.get('candidate')
        search = request.query_params.get('search')

        if status_value:
            cases = cases.filter(status=status_value)

        if priority:
            cases = cases.filter(priority=priority)

        if candidate_id:
            cases = cases.filter(candidate_id=candidate_id)

        if search:
            cases = cases.filter(
            case_number__icontains=search
            ) | cases.filter(
            candidate__candidate_code__icontains=search
            ) | cases.filter(
            candidate__first_name__icontains=search
            ) | cases.filter(
            candidate__last_name__icontains=search
            ) | cases.filter(
            candidate__email__icontains=search
            )
        serializer = BGVCaseSerializer(cases, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = BGVCaseSerializer(data=request.data)

        if serializer.is_valid():
            case = serializer.save(
                created_by=request.user
            )

            create_audit_log(
                user=request.user,
                case=case,
                action=AuditLog.Action.CASE_CREATED,
                description=(
                    f'BGV case {case.case_number} '
                    f'was created successfully.'
                )
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class BGVCaseDetailView(APIView):
    permission_classes = [IsAdminOrHR]

    def get_object(self, pk):
        try:
            return BGVCase.objects.select_related(
                'candidate',
                'assigned_to',
                'created_by',
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return None

    def get(self, request, pk):
        case = self.get_object(pk)

        if case is None:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BGVCaseSerializer(case)

        return Response(serializer.data)

    def put(self, request, pk):
        case = self.get_object(pk)

        if case is None:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BGVCaseSerializer(
            case,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        case = self.get_object(pk)

        if case is None:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BGVCaseSerializer(
            case,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        case = self.get_object(pk)

        if case is None:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        case.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

class BGVCaseAssignView(APIView):
    permission_classes = [IsAdminOrHR]

    def post(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate',
                'assigned_to',
                'created_by',
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BGVCaseAssignmentSerializer(
            data=request.data
        )

        if serializer.is_valid():
            verifier = serializer.validated_data['assigned_to']

            case.assigned_to = verifier

            if case.status == BGVCase.Status.OPEN:
                case.status = BGVCase.Status.IN_PROGRESS

            case.save(
                update_fields=[
                    'assigned_to',
                    'status',
                    'updated_at',
                ]
            )
            create_audit_log(
                user=request.user,
                case=case,
                action=AuditLog.Action.CASE_ASSIGNED,
                description=(
                    f'BGV case {case.case_number} '
                    f'was assigned to '
                    f'{case.assigned_to.username}.'
                )
            )

            return Response(
                BGVCaseSerializer(case).data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class MyAssignedBGVCasesView(APIView):
    permission_classes = [IsVerifier]

    def get(self, request):
        cases = (
            BGVCase.objects
            .select_related(
                'candidate',
                'assigned_to',
                'created_by',
            )
            .filter(
                assigned_to=request.user
            )
            .order_by('-created_at')
        )

        serializer = BGVCaseSerializer(
            cases,
            many=True
        )

        return Response(serializer.data)

class BGVCaseProcessView(APIView):
    permission_classes = [IsVerifier]

    def post(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate',
                'assigned_to',
                'created_by',
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if case.assigned_to != request.user:
            return Response(
                {'detail': 'You are not assigned to this BGV case.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = BGVCaseProcessingSerializer(
            data=request.data
        )

        if serializer.is_valid():
            case.status = serializer.validated_data['status']
            case.remarks = serializer.validated_data.get(
                'remarks',
                case.remarks
            )

            case.save(
                update_fields=[
                    'status',
                    'remarks',
                    'updated_at',
                ]
            )

            create_audit_log(
                user=request.user,
                case=case,
                action=AuditLog.Action.CASE_PROCESSED,
                description=(
                    f'BGV case {case.case_number} '
                    f'was processed and updated to '
                    f'{case.status}.'
                )
            )

            return Response(
                BGVCaseSerializer(case).data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class CreateCaseVerificationsView(APIView):
    permission_classes = [IsAdminOrHR]

    def post(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CreateCaseVerificationsSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        verification_types = serializer.validated_data.get(
            'verification_types'
        )

        if not verification_types:
            verification_types = [
                Verification.VerificationType.EMPLOYMENT,
                Verification.VerificationType.EDUCATION,
                Verification.VerificationType.ADDRESS,
                Verification.VerificationType.IDENTITY,
            ]

        created_verifications = []

        for verification_type in verification_types:
            verification, created = Verification.objects.get_or_create(
                candidate=case.candidate,
                verification_type=verification_type
            )

            created_verifications.append(
                verification
            )

        return Response(
            {
                'case_number': case.case_number,
                'candidate_id': case.candidate.id,
                'created_verifications': [
                    {
                        'id': verification.id,
                        'verification_type': verification.verification_type,
                        'status': verification.status,
                    }
                    for verification in created_verifications
                ]
            },
            status=status.HTTP_201_CREATED
        )

class CaseVerificationSummaryView(APIView):
    permission_classes = [IsAdminOrHR]

    def get(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        verifications = (
            Verification.objects
            .filter(candidate=case.candidate)
            .order_by('verification_type')
        )

        summary = verifications.aggregate(
            total=Count('id'),
            pending=Count(
                'id',
                filter=Q(
                    status=Verification.Status.PENDING
                )
            ),
            in_progress=Count(
                'id',
                filter=Q(
                    status=Verification.Status.IN_PROGRESS
                )
            ),
            verified=Count(
                'id',
                filter=Q(
                    status=Verification.Status.VERIFIED
                )
            ),
            failed=Count(
                'id',
                filter=Q(
                    status=Verification.Status.FAILED
                )
            ),
            on_hold=Count(
                'id',
                filter=Q(
                    status=Verification.Status.ON_HOLD
                )
            ),
        )

        verification_data = [
            {
                'id': verification.id,
                'verification_type': verification.verification_type,
                'status': verification.status,
                'assigned_to': (
                    verification.assigned_to.username
                    if verification.assigned_to
                    else None
                ),
                'remarks': verification.remarks,
                'result': verification.result,
            }
            for verification in verifications
        ]

        return Response(
            {
                'case_id': case.id,
                'case_number': case.case_number,
                'candidate_id': case.candidate.id,
                'candidate_name': (
                    f"{case.candidate.first_name} "
                    f"{case.candidate.last_name}"
                ).strip(),
                'case_status': case.status,
                'summary': summary,
                'verifications': verification_data,
            },
            status=status.HTTP_200_OK
        )

class CaseStatusSyncView(APIView):
    permission_classes = [IsAdminOrHR]

    def post(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        verifications = Verification.objects.filter(
            candidate=case.candidate
        )

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
            new_status = BGVCase.Status.OPEN

        elif verified == total:
            new_status = BGVCase.Status.COMPLETED

        elif failed > 0 or on_hold > 0:
            new_status = BGVCase.Status.ON_HOLD

        elif in_progress > 0:
            new_status = BGVCase.Status.IN_PROGRESS

        else:
            new_status = BGVCase.Status.OPEN

        case.status = new_status

        case.save(
            update_fields=[
                'status',
                'updated_at',
            ]
        )

        return Response(
            {
                'case_id': case.id,
                'case_number': case.case_number,
                'status': case.status,
                'verification_summary': {
                    'total': total,
                    'verified': verified,
                    'in_progress': in_progress,
                    'failed': failed,
                    'on_hold': on_hold,
                }
            },
            status=status.HTTP_200_OK
        )


class CaseReportReadinessView(APIView):
    permission_classes = [IsAdminOrHR]

    def get(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        required_types = {
            Verification.VerificationType.EMPLOYMENT,
            Verification.VerificationType.EDUCATION,
            Verification.VerificationType.ADDRESS,
            Verification.VerificationType.IDENTITY,
        }

        verified_types = set(
            Verification.objects.filter(
                candidate=case.candidate,
                status=Verification.Status.VERIFIED
            ).values_list(
                'verification_type',
                flat=True
            )
        )

        missing_types = required_types - verified_types

        ready_for_final_report = not missing_types

        return Response(
            {
                'case_id': case.id,
                'case_number': case.case_number,
                'candidate_id': case.candidate.id,
                'case_status': case.status,
                'ready_for_final_report': ready_for_final_report,
                'missing_verifications': list(
                    missing_types
                ),
            },
            status=status.HTTP_200_OK
        )

class CaseFinalReportView(APIView):
    permission_classes = [IsAdminOrHR]

    def post(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        required_types = {
            Verification.VerificationType.EMPLOYMENT,
            Verification.VerificationType.EDUCATION,
            Verification.VerificationType.ADDRESS,
            Verification.VerificationType.IDENTITY,
        }

        verified_types = set(
            Verification.objects.filter(
                candidate=case.candidate,
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
                    'detail': 'Final report cannot be generated.',
                    'case_id': case.id,
                    'case_number': case.case_number,
                    'ready_for_final_report': False,
                    'missing_verifications': list(missing_types),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        report, created = Report.objects.get_or_create(
            candidate=case.candidate
        )

        report.status = Report.Status.FINAL

        report.summary = (
            f"Final BGV report generated for "
            f"{case.candidate.first_name} "
            f"{case.candidate.last_name}."
        )

        report.generated_at = timezone.now()

        report.save()

        return Response(
            {
                'message': 'Final BGV report generated successfully.',
                'case_id': case.id,
                'case_number': case.case_number,
                'report_id': report.id,
                'report_status': report.status,
                'created': created,
                'generated_at': report.generated_at,
            },
            status=status.HTTP_200_OK
        )

class CaseReportDetailView(APIView):
    permission_classes = [IsAdminOrHR]

    def get(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            report = Report.objects.get(
                candidate=case.candidate
            )
        except Report.DoesNotExist:
            return Response(
                {
                    'detail': 'Report not found for this BGV case.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        verifications = Verification.objects.filter(
            candidate=case.candidate
        ).values(
            'id',
            'verification_type',
            'status',
            'remarks',
            'result',
            'assigned_to_id',
            'created_at',
            'updated_at',
        )

        return Response(
            {
                'case': {
                    'id': case.id,
                    'case_number': case.case_number,
                    'status': case.status,
                    'priority': case.priority,
                },
                'candidate': {
                    'id': case.candidate.id,
                    'candidate_code': case.candidate.candidate_code,
                    'name': (
                        f"{case.candidate.first_name} "
                        f"{case.candidate.last_name}"
                    ).strip(),
                    'email': case.candidate.email,
                },
                'report': {
                    'id': report.id,
                    'status': report.status,
                    'summary': report.summary,
                    'generated_at': report.generated_at,
                },
                'verifications': verifications,
            },
            status=status.HTTP_200_OK
        )

class CaseReportExportView(APIView):
    permission_classes = [IsAdminOrHR]

    def get(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {
                    'detail': 'BGV case not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            report = Report.objects.get(
                candidate=case.candidate
            )
        except Report.DoesNotExist:
            return Response(
                {
                    'detail': 'Report not found for this BGV case.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if report.status != Report.Status.FINAL:
            return Response(
                {
                    'detail': 'Only FINAL reports can be exported.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        verifications = Verification.objects.filter(
            candidate=case.candidate
        ).values(
            'id',
            'verification_type',
            'status',
            'remarks',
            'result',
            'assigned_to_id',
            'created_at',
            'updated_at',
        )

        return Response(
            {
                'export_type': 'BGV_REPORT',
                'case': {
                    'id': case.id,
                    'case_number': case.case_number,
                    'status': case.status,
                    'priority': case.priority,
                },
                'candidate': {
                    'id': case.candidate.id,
                    'candidate_code': case.candidate.candidate_code,
                    'name': (
                        f"{case.candidate.first_name} "
                        f"{case.candidate.last_name}"
                    ).strip(),
                    'email': case.candidate.email,
                },
                'report': {
                    'id': report.id,
                    'status': report.status,
                    'summary': report.summary,
                    'generated_at': report.generated_at,
                },
                'verifications': list(verifications),
            },
            status=status.HTTP_200_OK
        )


class CaseReportPDFView(APIView):
    permission_classes = [IsAdminOrHR]

    def get(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {
                    'detail': 'BGV case not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            report = Report.objects.get(
                candidate=case.candidate
            )
        except Report.DoesNotExist:
            return Response(
                {
                    'detail': 'Report not found for this BGV case.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if report.status != Report.Status.FINAL:
            return Response(
                {
                    'detail': 'Only FINAL reports can be downloaded.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        verifications = Verification.objects.filter(
            candidate=case.candidate
        ).order_by(
            'verification_type'
        )

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        styles = getSampleStyleSheet()

        title_style = styles['Title']
        heading_style = styles['Heading2']
        normal_style = styles['BodyText']

        story = []

        story.append(
            Paragraph(
                'BACKGROUND VERIFICATION REPORT',
                title_style
            )
        )

        story.append(Spacer(1, 10))

        candidate_name = (
            f"{case.candidate.first_name} "
            f"{case.candidate.last_name}"
        ).strip()

        candidate_data = [
            ['Case Number', case.case_number],
            ['Candidate Name', candidate_name],
            ['Candidate Code', case.candidate.candidate_code],
            ['Candidate Email', case.candidate.email],
            ['Case Status', case.status],
            ['Priority', case.priority],
            ['Report Status', report.status],
            ['Generated At', str(report.generated_at)],
        ]

        candidate_table = Table(
            candidate_data,
            colWidths=[45 * mm, 115 * mm]
        )

        candidate_table.setStyle(
            TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ])
        )

        story.append(candidate_table)
        story.append(Spacer(1, 15))

        story.append(
            Paragraph(
                'Report Summary',
                heading_style
            )
        )

        story.append(
            Paragraph(
                report.summary or 'No summary available.',
                normal_style
            )
        )

        story.append(Spacer(1, 15))

        story.append(
            Paragraph(
                'Verification Details',
                heading_style
            )
        )

        verification_cell_style = styles['BodyText']
        verification_cell_style.fontSize = 7
        verification_cell_style.leading = 9

        verification_header_style = styles['BodyText']
        verification_header_style.fontSize = 7
        verification_header_style.leading = 9

        verification_data = [
            [
            Paragraph('<b>Type</b>',     verification_header_style),
            Paragraph('<b>Status</b>',     verification_header_style),
            Paragraph('<b>Remarks</b>',     verification_header_style),
            Paragraph('<b>Result</b>',     verification_header_style),
        ]
    ]

        for verification in verifications:
            verification_data.append([
                Paragraph(
                    verification.get_verification_type_display(),
                verification_cell_style
            ),
            Paragraph(
                verification.get_status_display(),
                verification_cell_style
            ),
            Paragraph(
                verification.remarks or '-',
                verification_cell_style
            ),
            Paragraph(
                verification.result or '-',
                verification_cell_style
            ),
        ])

        verification_table = Table(
            verification_data,
            colWidths=[
                32 * mm,
                28 * mm,
                55 * mm,
                55 * mm,
            ],
            repeatRows=1,
        )

        verification_table.setStyle(
            TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.        grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.        lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ])
        )

        verification_table.setStyle(
            TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ])
        )

        story.append(verification_table)

        document.build(story)

        buffer.seek(0)

        filename = (
            f"BGV_Report_{case.case_number}.pdf"
        )

        return FileResponse(
            buffer,
            as_attachment=True,
            filename=filename,
            content_type='application/pdf'
        )

class ClientCaseReportPDFView(APIView):
    permission_classes = [IsClient]

    def get(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate',
                'candidate__client'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {
                    'detail': 'BGV case not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if case.candidate.client != request.user:
            return Response(
                {
                    'detail': 'You do not have access to this BGV case.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            report = Report.objects.get(
                candidate=case.candidate
            )
        except Report.DoesNotExist:
            return Response(
                {
                    'detail': 'Report not found for this BGV case.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if report.status != Report.Status.FINAL:
            return Response(
                {
                    'detail': 'Only FINAL reports can be downloaded.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        verifications = Verification.objects.filter(
            candidate=case.candidate
        ).order_by(
            'verification_type'
        )

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        styles = getSampleStyleSheet()

        story = []

        story.append(
            Paragraph(
                'BACKGROUND VERIFICATION REPORT',
                styles['Title']
            )
        )

        story.append(Spacer(1, 10))

        candidate_name = (
            f"{case.candidate.first_name} "
            f"{case.candidate.last_name}"
        ).strip()

        candidate_data = [
            ['Case Number', case.case_number],
            ['Candidate Name', candidate_name],
            ['Candidate Code', case.candidate.candidate_code],
            ['Candidate Email', case.candidate.email],
            ['Case Status', case.status],
            ['Priority', case.priority],
            ['Report Status', report.status],
            ['Generated At', str(report.generated_at)],
        ]

        candidate_table = Table(
            candidate_data,
            colWidths=[45 * mm, 115 * mm]
        )

        candidate_table.setStyle(
            TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ])
        )

        story.append(candidate_table)
        story.append(Spacer(1, 15))

        story.append(
            Paragraph(
                'Report Summary',
                styles['Heading2']
            )
        )

        story.append(
            Paragraph(
                report.summary or 'No summary available.',
                styles['BodyText']
            )
        )

        story.append(Spacer(1, 15))

        story.append(
            Paragraph(
                'Verification Details',
                styles['Heading2']
            )
        )
        verification_cell_style = styles['BodyText']
        verification_cell_style.fontSize = 7
        verification_cell_style.leading = 9

        verification_header_style = styles['BodyText']
        verification_header_style.fontSize = 7
        verification_header_style.leading = 9

        verification_data = [
            [
                Paragraph('<b>Status</b>',         verification_header_style),
                Paragraph('<b>Type</b>',         verification_header_style),
                Paragraph('<b>Remarks</b>',         verification_header_style),
                Paragraph('<b>Result</b>',         verification_header_style),
            ]
        ]

        for verification in verifications:
            verification_data.append([
                Paragraph(
                    verification.         get_verification_type_display(),
                    verification_cell_style
                ),
                Paragraph(
                    verification.get_status_display(),
                    verification_cell_style
                ),
                Paragraph(
                    verification.remarks or '-',
                    verification_cell_style
                ),
                Paragraph(
                    verification.result or '-',
                    verification_cell_style
                ),
            ])

        verification_table = Table(
            verification_data,
            colWidths=[
                32 * mm,
                28 * mm,
                55 * mm,
                55 * mm,
            ],
            repeatRows=1,
        )

        verification_table.setStyle(
            TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.        grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.        lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ])
        )


        verification_table.setStyle(
            TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ])
        )

        story.append(verification_table)

        document.build(story)

        buffer.seek(0)

        filename = (
            f"BGV_Report_{case.case_number}.pdf"
        )

        return FileResponse(
            buffer,
            as_attachment=True,
            filename=filename,
            content_type='application/pdf'
        )

class CandidateCaseReportPDFView(APIView):
    permission_classes = [IsCandidate]

    def get(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate',
                'candidate__user'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {
                    'detail': 'BGV case not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if case.candidate.user != request.user:
            return Response(
                {
                    'detail': 'You do not have access to this BGV case.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            report = Report.objects.get(
                candidate=case.candidate
            )
        except Report.DoesNotExist:
            return Response(
                {
                    'detail': 'Report not found for this BGV case.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if report.status != Report.Status.FINAL:
            return Response(
                {
                    'detail': 'Only FINAL reports can be downloaded.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        verifications = Verification.objects.filter(
            candidate=case.candidate
        ).order_by(
            'verification_type'
        )

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        styles = getSampleStyleSheet()

        story = []

        story.append(
            Paragraph(
                'BACKGROUND VERIFICATION REPORT',
                styles['Title']
            )
        )

        story.append(Spacer(1, 10))

        candidate_name = (
            f"{case.candidate.first_name} "
            f"{case.candidate.last_name}"
        ).strip()

        candidate_data = [
            ['Case Number', case.case_number],
            ['Candidate Name', candidate_name],
            ['Candidate Code', case.candidate.candidate_code],
            ['Candidate Email', case.candidate.email],
            ['Case Status', case.status],
            ['Priority', case.priority],
            ['Report Status', report.status],
            ['Generated At', str(report.generated_at)],
        ]

        candidate_table = Table(
            candidate_data,
            colWidths=[45 * mm, 115 * mm]
        )

        candidate_table.setStyle(
            TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ])
        )

        story.append(candidate_table)
        story.append(Spacer(1, 15))

        story.append(
            Paragraph(
                'Report Summary',
                styles['Heading2']
            )
        )

        story.append(
            Paragraph(
                report.summary or 'No summary available.',
                styles['BodyText']
            )
        )

        story.append(Spacer(1, 15))

        story.append(
            Paragraph(
                'Verification Details',
                styles['Heading2']
            )
        )

        verification_cell_style = styles['BodyText']
        verification_cell_style.fontSize = 7
        verification_cell_style.leading = 9

        verification_header_style = styles['BodyText']
        verification_header_style.fontSize = 7
        verification_header_style.leading = 9

        verification_data = [
            [
                Paragraph('<b>Type</b>', verification_header_style),
                Paragraph('<b>Status</b>', verification_header_style),
                Paragraph('<b>Remarks</b>', verification_header_style),
                Paragraph('<b>Result</b>', verification_header_style),
            ]
        ]

        for verification in verifications:
            verification_data.append([
                Paragraph(
                    verification.get_verification_type_display(),
                    verification_cell_style
                ),
                Paragraph(
                    verification.get_status_display(),
                    verification_cell_style
                ),
                Paragraph(
                    verification.remarks or '-',
                    verification_cell_style
                ),
                Paragraph(
                    verification.result or '-',
                    verification_cell_style
                ),
            ])

        verification_table = Table(
            verification_data,
            colWidths=[
                32 * mm,
                28 * mm,
                55 * mm,
                55 * mm,
            ],
            repeatRows=1,
        )

        verification_table.setStyle(
            TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ])
        )

        story.append(verification_table)

        document.build(story)

        buffer.seek(0)

        filename = (
            f"BGV_Report_{case.case_number}.pdf"
        )

        return FileResponse(
            buffer,
            as_attachment=True,
            filename=filename,
            content_type='application/pdf'
        )

class BGVCaseDashboardView(APIView):
    permission_classes = [IsAdminOrHR]

    def get(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate',
                'assigned_to'
            ).get(pk=pk)
            case_age = timezone.now() - case.created_at

            case_age_days = case_age.days
            case_age_hours = round(
                case_age.total_seconds() / 3600,
                2
            )
        # Case SLA / Aging Status
            if case_age_days <= 2:
               case_aging_status = 'NORMAL'
               case_aging_label = 'Case is within normal aging period'
            elif case_age_days <= 5:
                case_aging_status = 'AGING'
                case_aging_label = 'Case is getting older'
            else:
                case_aging_status = 'OVERDUE'
                case_aging_label = 'Case has exceeded the normal aging period'
                # Case Escalation Indicator

            # Case SLA Deadline
            if case.priority.upper() == 'HIGH':
                sla_target_days = 3
            else:
                sla_target_days = 7

            sla_deadline = case.created_at + timedelta(days=sla_target_days)
            now = timezone.now()

            if now > sla_deadline:
                sla_status = 'OVERDUE'
            elif now.date() == sla_deadline.date():
                sla_status = 'DUE'
            else:
                sla_status = 'ON_TRACK'

            days_remaining = max(
                0,
                (sla_deadline.date() - now.date()).days
            )
            # Case SLA Summary
            if sla_target_days > 0:
                elapsed_days = max(
                    0,
                    (now.date() - case.created_at.date()).days
                )

                sla_percentage = round(
                    min((elapsed_days / sla_target_days) * 100, 100),
                                2
                )
            else:
                sla_percentage = 0

            is_sla_overdue = sla_status == 'OVERDUE'
            # Case SLA Risk Level
            if sla_status == 'OVERDUE':
                sla_risk_level = 'CRITICAL'
            elif days_remaining <= 1:
                sla_risk_level = 'HIGH'
            elif days_remaining <= 2:
                sla_risk_level = 'MEDIUM'
            else:
                sla_risk_level = 'LOW'


        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        # Overall Case Risk Level

        verifications = Verification.objects.filter(
            candidate=case.candidate
        )
        document_details = [
            {
                'id': document.id,
                'document_name': document.document_name,
                'document_type': document.document_type,
                'candidate_id': document.candidate.id,
                'verification_id': (
                    document.verification.id
                    if document.verification
                    else None
                ),
                'status': document.status,
                'uploaded_by': (
                    document.uploaded_by.username
                    if document.uploaded_by
                    else None
                ),
                'uploaded_at': document.uploaded_at,
                'updated_at': document.updated_at,
            }
            for document in Document.objects.filter(
                candidate=case.candidate
            )
        ]
        document_summary = {}

        for verification in verifications:
            documents = Document.objects.filter(
                verification=verification
            )

            document_summary[verification.id] = {
                'total': documents.count(),
                'verified': documents.filter(
                    status=Document.Status.VERIFIED
                ).count(),
                'pending': documents.filter(
                    status=Document.Status.PENDING
                ).count(),
                'rejected': documents.filter(
                    status=Document.Status.REJECTED
                ).count(),
            }

        total_documents = Document.objects.filter(
            candidate=case.candidate
            ).count()

        verified_documents = Document.objects.filter(
            candidate=case.candidate,
            status=Document.Status.VERIFIED
        ).count()

        pending_documents = Document.objects.filter(
            candidate=case.candidate,
            status=Document.Status.PENDING
        ).count()

        rejected_documents = Document.objects.filter(
            candidate=case.candidate,
            status=Document.Status.REJECTED
        ).count()
        document_verified_percentage = (
            round(
                (verified_documents / total_documents) * 100,
                2
            )
            if total_documents > 0
            else 0
        )
        last_verification_update = verifications.order_by(
            '-updated_at'
        ).values_list(
            'updated_at',
            flat=True
        ).first()

        last_document_update = Document.objects.filter(
            candidate=case.candidate
        ).order_by(
            '-updated_at'
        ).values_list(
            'updated_at',
            flat=True
        ).first()

        if total_documents == 0:
            document_verification_status = 'PENDING'
        elif rejected_documents > 0:
            document_verification_status = 'REJECTED'
        elif verified_documents == total_documents:
            document_verification_status = 'COMPLETED'
        else:
            document_verification_status = 'IN_PROGRESS'

        document_ready = (
            total_documents > 0
            and verified_documents == total_documents
        )

        if total_documents == 0:
            document_readiness_reason = 'No documents uploaded'
        elif rejected_documents > 0:
            document_readiness_reason = 'One or more documents are rejected'
        elif pending_documents > 0:
            document_readiness_reason = 'One or more documents are pending'
        else:
            document_readiness_reason = 'All documents are verified'
        verification_type_summary = [
            {
                'type': verification.verification_type,
                'status': verification.status,
            }
            for verification in verifications
        ]
        required_verification_types = {
            Verification.VerificationType.EMPLOYMENT,
            Verification.VerificationType.EDUCATION,
            Verification.VerificationType.ADDRESS,
            Verification.VerificationType.IDENTITY,
        }

        verified_types = set(
            verifications.filter(
                status=Verification.Status.VERIFIED
            ).values_list(
                'verification_type',
                flat=True
            )
        )

        completed_required_types = (
            required_verification_types & verified_types
        )

        total = verifications.count()

        verified = verifications.filter(
            status=Verification.Status.VERIFIED
        ).count()

        pending = verifications.filter(
            status=Verification.Status.PENDING
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

        # Case Escalation Indicator
        if (
            case_aging_status == 'OVERDUE'
            or case.priority.upper() == 'HIGH'
            or failed > 0
            or on_hold > 0
            or rejected_documents > 0
        ):
            escalation_status = 'ESCALATION_REQUIRED'
            escalation_label = 'Case requires escalation'
        else:
            escalation_status = 'NO_ESCALATION'
            escalation_label = 'No escalation required'

        # Case Risk Score
        case_risk_score = 0

        if case.priority.upper() == 'HIGH':
            case_risk_score += 20

        if failed > 0:
            case_risk_score += 40

        if on_hold > 0:
            case_risk_score += 20

        if rejected_documents > 0:
            case_risk_score += 30

        if sla_risk_level == 'CRITICAL':
            case_risk_score += 30
        elif sla_risk_level == 'HIGH':
            case_risk_score += 15

        case_risk_score = min(case_risk_score, 100)

        # Overall Case Risk Level
        case_risk_reasons = []

        if case.priority.upper() == 'HIGH':
           case_risk_reasons.append('Case has high priority')

        if failed > 0:
            case_risk_reasons.append('One or more verifications failed')

        if on_hold > 0:
            case_risk_reasons.append('One or more verifications are on hold')

        if rejected_documents > 0:
            case_risk_reasons.append('One or more documents are rejected')

        if sla_risk_level == 'CRITICAL':
            case_risk_reasons.append('SLA is overdue')
        elif sla_risk_level == 'HIGH':
            case_risk_reasons.append('SLA deadline is near')

        if (
            sla_risk_level == 'CRITICAL'
            or failed > 0
            or rejected_documents > 0
        ):
           case_risk_level = 'CRITICAL'
        elif (
            case.priority.upper() == 'HIGH'
            or on_hold > 0
            or sla_risk_level == 'HIGH'
            ):
            case_risk_level = 'HIGH'
        elif sla_risk_level == 'MEDIUM':
            case_risk_level = 'MEDIUM'
        else:
            case_risk_level = 'LOW'

        report = Report.objects.filter(
        candidate=case.candidate
        ).first()


        verified_percentage = (
            round((verified / total) * 100, 2)
            if total > 0
            else 0
        )
        unassigned_verifications = [
        {
            'id': verification.id,
            'type': verification.verification_type,
            'status': verification.status,
        }
        for verification in verifications
        if verification.assigned_to is None
        ]
        if total == 0:
            case_health_status = 'PENDING'
            case_health_label = 'No verifications available'

        elif failed > 0:
            case_health_status = 'FAILED'
            case_health_label = 'One or more verifications failed'

        elif on_hold > 0:
            case_health_status = 'ON_HOLD'
            case_health_label = 'One or more verifications are on hold'

        elif in_progress > 0:
            case_health_status = 'IN_PROGRESS'
            case_health_label = 'Verification is in progress'

        elif verified == total:
            case_health_status = 'COMPLETED'
            case_health_label = 'All verifications completed'

        else:
            case_health_status = 'PENDING'
            case_health_label = 'Verification is pending'

        if case.priority.upper() == 'HIGH':
            attention_required = True
        else:
            attention_required = False

        if (
            case.priority.upper() == 'HIGH'
            or failed > 0
            or on_hold > 0
            or rejected_documents > 0
            or pending_documents > 0
        ):
            case_attention_status = 'ATTENTION_REQUIRED'
        else:
            case_attention_status = 'NORMAL'

        assigned = verifications.filter(
            assigned_to__isnull=False
        ).count()

        unassigned = verifications.filter(
            assigned_to__isnull=True
        ).count()

        assigned_percentage = (
            round((assigned / total) * 100, 2)
            if total > 0
            else 0
        )

        # Final Case Decision Summary
        verification_complete = (
            required_verification_types ==completed_required_types
        )

        report_ready = (
            report is not None
            and report.status == Report.Status.FINAL
        )

        # Final Case Decision Summary
        verification_complete = (
            required_verification_types == completed_required_types
        )

        report_ready = (
            report is not None
            and report.status == Report.Status.FINAL
        )

        if case_risk_level == 'CRITICAL':
            final_case_status = 'REVIEW_REQUIRED'
            final_case_label = 'Case requires review before closure'

        elif not verification_complete:
            final_case_status = 'VERIFICATION_PENDING'
            final_case_label = 'Required verifications are pending'

        elif not document_ready:
            final_case_status = 'DOCUMENTS_PENDING'
            final_case_label = 'Required documents are pending'

        elif not report_ready:
            final_case_status = 'REPORT_PENDING'
            final_case_label = 'Final report is not available'

        else:
            final_case_status = 'READY_TO_CLOSE'
            final_case_label = 'Case is ready to close'


        return Response({
            'case': {
                'id': case.id,
                'case_number': case.case_number,
                'status': case.status,
                'priority': case.priority,
                'assigned_verifier': {
                    'id' : case.assigned_to.id,
                    'username' : case.assigned_to.username,
                    'email' : case.assigned_to.email,
                    'role' : case.assigned_to.role,
                } if case.assigned_to else None,
            },

            'candidate': {
                'id': case.candidate.id,
                'candidate_code': case.candidate.candidate_code,
                'name': (
                    f"{case.candidate.first_name} "
                    f"{case.candidate.last_name}"
                ).strip(),
                'email': case.candidate.email,
            },

            'verification_summary': {
                'total': total,
                'verified': verified,
                'pending': pending,
                'in_progress': in_progress,
                'failed': failed,
                'on_hold': on_hold,
                'verified_percentage': verified_percentage,
                'progress': {
                    'completed': verified,
                    'total': total,
                    'percentage': verified_percentage,
                },

            },
            'assignment_summary': {
            'total': total,
            'assigned': assigned,
            'unassigned': unassigned,
            'assigned_percentage': assigned_percentage,
            },
            'document_summary': {
            'total': total_documents,
            'verified': verified_documents,
            'pending': pending_documents,
            'rejected': rejected_documents,
            },
            'document_verification': {
                'total': total_documents,
                'verified': verified_documents,
                'pending': pending_documents,
                'rejected': rejected_documents,
                'verified_percentage': document_verified_percentage,
                'status': document_verification_status,
            },
            'document_readiness': {
            'ready': document_ready,
            'reason': document_readiness_reason,
            },
            'activity_summary': {
            'case_created_at': case.created_at,
            'case_updated_at': case.updated_at,
            'last_verification_update': last_verification_update,
            'last_document_update': last_document_update,
            },
            'case_duration': {
            'created_at': case.created_at,
            'age_days': case_age_days,
            'age_hours': case_age_hours,
            },
            'case_aging': {
            'status': case_aging_status,
            'label': case_aging_label,
            'age_days': case_age_days,
            },
            'case_escalation': {
                'status': escalation_status,
                'label': escalation_label,
                'escalation_required': (
                    escalation_status == 'ESCALATION_REQUIRED'
                ),
            },
            'case_sla': {
                'target_days' : sla_target_days,                'deadline': sla_deadline,
                'days_remaining': days_remaining,
                'status': sla_status,
                'is_overdue': is_sla_overdue,
                'sla_percentage': sla_percentage,
                'risk_level' : sla_risk_level,
            },
            'case_risk': {
                'level': case_risk_level,
                'reasons': case_risk_reasons,
            },
            'case_risk_score': {
                'score': case_risk_score,
                'level': case_risk_level,
            },
            'case_risk_summary': {
                'score': case_risk_score,
                'level': case_risk_level,
                'attention_required': case_risk_level in [
                    'HIGH',
                    'CRITICAL'
                ],
                        'reason_count': len(case_risk_reasons),
                'reasons': case_risk_reasons,
            },
            'final_case_summary': {
                'status': final_case_status,
                'label': final_case_label,
                'risk_level': case_risk_level,
                'verification_complete': verification_complete,
                'documents_ready': document_ready,
                'report_ready': report_ready,
            },
            'case_attention': {
                'status': case_attention_status,
                'attention_required': (
                    case_attention_status == 'ATTENTION_REQUIRED'
                ),
            },
            'document_details': document_details,
            'unassigned_verifications': unassigned_verifications,
            'verification_type_summary': verification_type_summary,
            'verification_completion': {
            'required_types': len        (required_verification_types),
            'completed_types': len        (completed_required_types),
            'all_required_completed': (
                required_verification_types
                == completed_required_types
            ),
            },
            'case_health': {
            'status': case_health_status,
            'label': case_health_label,
            },
            'priority_info': {
            'priority': case.priority,
            'attention_required': attention_required,
            },
            'verification_details': [
                {
                    'id': verification.id,
                    'type': verification.verification_type,
                    'status': verification.status,
                    'document_summary': document_summary.get(
                        verification.id,
                        {
                            'total': 0,
                            'verified': 0,
                            'pending': 0,
                            'rejected': 0,
                        }
                    ),
                    'assignment_status': (
                        'ASSIGNED'
                    if verification.assigned_to
                    else 'UNASSIGNED'
                    ),
                    'assigned_to': (
                        verification.assigned_to.username
                        if verification.assigned_to
                        else None
                    ),
                    'assigned_verifier': {
                        'id': verification.assigned_to.id,
                        'username': verification.assigned_to.username,
                        'email': verification.assigned_to.email,
                        'role': verification.assigned_to.role,
                    } if verification.assigned_to else None,
                    'remarks': verification.remarks,
                    'result': verification.result,
                    'created_at' : verification.created_at,
                    'updated_at': verification.updated_at,
                }
                for verification in verifications
            ],

        'report': {
        'id': report.id if report else None,
        'status': report.status if report else None,
        'summary': report.summary if report else None,
        'generated_at': report.generated_at if report else None,
        'ready_for_final_report': (
            required_verification_types
            == completed_required_types
        ),
        'download_available': (
            report is not None
            and report.status == Report.Status.FINAL
        ),
        'pdf_url': (
            f'/api/cases/{case.id}/report/pdf/'
            if report is not None
            and report.status == Report.Status.FINAL
            else None
        ),
    },
        }, status=status.HTTP_200_OK)

class CaseVerificationTimelineView(APIView):

    permission_classes = [IsAdminOrHR]

    def get(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        verifications = Verification.objects.filter(
            candidate=case.candidate
        ).select_related(
            'assigned_to'
        ).order_by(
            '-updated_at'
        )

        timeline = []

        for verification in verifications:
            timeline.append({
                'verification_id': verification.id,
                'verification_type': verification.verification_type,
                'status': verification.status,
                'assigned_to': (
                    verification.assigned_to.username
                    if verification.assigned_to
                    else None
                ),
                'remarks': verification.remarks,
                'result': verification.result,
                'created_at': verification.created_at,
                'updated_at': verification.updated_at,
            })

        return Response({
            'case_id': case.id,
            'case_number': case.case_number,
            'candidate_id': case.candidate.id,
            'candidate_name': (
                f"{case.candidate.first_name} "
                f"{case.candidate.last_name}"
            ).strip(),
            'timeline': timeline,
        }, status=status.HTTP_200_OK)

class ClientBGVCaseDashboardView(APIView):
    permission_classes = [IsClient]

    def get(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate',
                'candidate__client',
                'assigned_to'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if case.candidate.client != request.user:
            return Response(
                {
                    'detail':
                    'You do not have access to this BGV case.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        verifications = Verification.objects.filter(
            candidate=case.candidate
        ).select_related(
            'assigned_to'
        )

        total = verifications.count()

        verified = verifications.filter(
            status=Verification.Status.VERIFIED
        ).count()

        pending = verifications.filter(
            status=Verification.Status.PENDING
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

        verified_percentage = (
            round((verified / total) * 100, 2)
            if total > 0
            else 0
        )

        report = getattr(
            case.candidate,
            'report',
            None
        )

        return Response({
            'case': {
                'id': case.id,
                'case_number': case.case_number,
                'status': case.status,
                'priority': case.priority,
            },

            'candidate': {
                'id': case.candidate.id,
                'candidate_code':
                    case.candidate.candidate_code,
                'name': (
                    f"{case.candidate.first_name} "
                    f"{case.candidate.last_name}"
                ).strip(),
                'email': case.candidate.email,
            },

            'verification_summary': {
                'total': total,
                'verified': verified,
                'pending': pending,
                'in_progress': in_progress,
                'failed': failed,
                'on_hold': on_hold,
                'verified_percentage':
                    verified_percentage,
            },

            'report': {
                'id': report.id if report else None,
                'status':
                    report.status if report else None,
            },
        }, status=status.HTTP_200_OK)

class VerifierBGVCaseDashboardView(APIView):
    permission_classes = [IsVerifier]

    def get(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate',
                'assigned_to'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if case.assigned_to != request.user:
            return Response(
                {
                    'detail':
                    'You do not have access to this BGV case.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        verifications = Verification.objects.filter(
            candidate=case.candidate
        ).select_related(
            'assigned_to'
        )

        total = verifications.count()

        verified = verifications.filter(
            status=Verification.Status.VERIFIED
        ).count()

        pending = verifications.filter(
            status=Verification.Status.PENDING
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

        verified_percentage = (
            round((verified / total) * 100, 2)
            if total > 0
            else 0
        )

        report = getattr(
            case.candidate,
            'report',
            None
        )

        return Response({
            'case': {
                'id': case.id,
                'case_number': case.case_number,
                'status': case.status,
                'priority': case.priority,
            },

            'candidate': {
                'id': case.candidate.id,
                'candidate_code':
                    case.candidate.candidate_code,
                'name': (
                    f"{case.candidate.first_name} "
                    f"{case.candidate.last_name}"
                ).strip(),
                'email': case.candidate.email,
            },

            'verification_summary': {
                'total': total,
                'verified': verified,
                'pending': pending,
                'in_progress': in_progress,
                'failed': failed,
                'on_hold': on_hold,
                'verified_percentage':
                    verified_percentage,
            },

            'verification_details': [
                {
                    'id': verification.id,
                    'type': verification.verification_type,
                    'status': verification.status,
                    'remarks': verification.remarks,
                    'result': verification.result,
                    'updated_at':
                        verification.updated_at,
                }
                for verification in verifications
            ],

            'report': {
                'id': report.id if report else None,
                'status':
                    report.status if report else None,
            },
        }, status=status.HTTP_200_OK)

class CaseClosureReadinessView(APIView):
    permission_classes = [IsAdminOrHR]

    def get(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        verifications = Verification.objects.filter(
            candidate=case.candidate
        )

        required_verification_types = {
            Verification.VerificationType.EMPLOYMENT,
            Verification.VerificationType.EDUCATION,
            Verification.VerificationType.ADDRESS,
            Verification.VerificationType.IDENTITY,
        }

        verified_types = set(
            verifications.filter(
                status=Verification.Status.VERIFIED
            ).values_list(
                'verification_type',
                flat=True
            )
        )

        completed_required_types = (
            required_verification_types & verified_types
        )

        verification_complete = (
            required_verification_types
            == completed_required_types
        )

        total_documents = Document.objects.filter(
            candidate=case.candidate
        ).count()

        verified_documents = Document.objects.filter(
            candidate=case.candidate,
            status=Document.Status.VERIFIED
        ).count()

        pending_documents = Document.objects.filter(
            candidate=case.candidate,
            status=Document.Status.PENDING
        ).count()

        rejected_documents = Document.objects.filter(
            candidate=case.candidate,
            status=Document.Status.REJECTED
        ).count()

        document_ready = (
            total_documents > 0
            and verified_documents == total_documents
        )

        report = Report.objects.filter(
            candidate=case.candidate
        ).first()

        report_ready = (
            report is not None
            and report.status == Report.Status.FINAL
        )

        closure_reasons = []

        if not verification_complete:
            closure_reasons.append(
                'Required verifications are pending'
            )

        if not document_ready:
            if total_documents == 0:
                closure_reasons.append(
                    'No documents uploaded'
                )
            elif rejected_documents > 0:
                closure_reasons.append(
                    'One or more documents are rejected'
                )
            elif pending_documents > 0:
                closure_reasons.append(
                    'One or more documents are pending'
                )

        if not report_ready:
            closure_reasons.append(
                'Final report is not available'
            )

        if case.status != BGVCase.Status.COMPLETED:
            closure_reasons.append(
                'Case status is not COMPLETED'
            )

        can_close = (
            verification_complete
            and document_ready
            and report_ready
            and case.status == BGVCase.Status.COMPLETED
        )

        if can_close:
            closure_status = 'READY_TO_CLOSE'
            closure_label = 'Case is ready to close'
        else:
            closure_status = 'CLOSURE_BLOCKED'
            closure_label = 'Case cannot be closed yet'

        return Response(
            {
                'case': {
                    'id': case.id,
                    'case_number': case.case_number,
                    'status': case.status,
                },
                'closure_readiness': {
                    'can_close': can_close,
                    'status': closure_status,
                    'label': closure_label,
                    'verification_complete': verification_complete,
                    'documents_ready': document_ready,
                    'report_ready': report_ready,
                    'case_completed': (
                        case.status == BGVCase.Status.COMPLETED
                    ),
                },
                'closure_reasons': closure_reasons,
            },
            status=status.HTTP_200_OK
        )

class CaseCloseView(APIView):
    permission_classes = [IsAdminOrHR]

    def post(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        verifications = Verification.objects.filter(
            candidate=case.candidate
        )

        required_verification_types = {
            Verification.VerificationType.EMPLOYMENT,
            Verification.VerificationType.EDUCATION,
            Verification.VerificationType.ADDRESS,
            Verification.VerificationType.IDENTITY,
        }

        verified_types = set(
            verifications.filter(
                status=Verification.Status.VERIFIED
            ).values_list(
                'verification_type',
                flat=True
            )
        )

        verification_complete = (
            required_verification_types == verified_types
        )

        total_documents = Document.objects.filter(
            candidate=case.candidate
        ).count()

        verified_documents = Document.objects.filter(
            candidate=case.candidate,
            status=Document.Status.VERIFIED
        ).count()

        document_ready = (
            total_documents > 0
            and verified_documents == total_documents
        )

        report = Report.objects.filter(
            candidate=case.candidate
        ).first()

        report_ready = (
            report is not None
            and report.status == Report.Status.FINAL
        )

        closure_reasons = []

        if not verification_complete:
            closure_reasons.append(
                'Required verifications are pending'
            )

        if not document_ready:
            if total_documents == 0:
                closure_reasons.append(
                    'No documents uploaded'
                )
            else:
                pending_documents = Document.objects.filter(
                    candidate=case.candidate,
                    status=Document.Status.PENDING
                ).count()

                rejected_documents = Document.objects.filter(
                    candidate=case.candidate,
                    status=Document.Status.REJECTED
                ).count()

                if rejected_documents > 0:
                    closure_reasons.append(
                        'One or more documents are rejected'
                    )
                elif pending_documents > 0:
                    closure_reasons.append(
                        'One or more documents are pending'
                    )

        if not report_ready:
            closure_reasons.append(
                'Final report is not available'
            )

        if case.status != BGVCase.Status.COMPLETED:
            closure_reasons.append(
                'Case status is not COMPLETED'
            )

        if closure_reasons:
            return Response(
                {
                    'detail': 'Case cannot be closed.',
                    'case_id': case.id,
                    'case_number': case.case_number,
                    'can_close': False,
                    'closure_reasons': closure_reasons,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        case.status = BGVCase.Status.CLOSED
        case.save(update_fields=['status', 'updated_at'])

        create_audit_log(
            user=request.user,
            case=case,
            action=AuditLog.Action.CASE_CLOSED,
            description=(
                f'BGV case {case.case_number} '
                f'was closed successfully.'
            )
        )

        return Response(
            {
                'message': 'BGV case closed successfully.',
                'case': {
                    'id': case.id,
                    'case_number': case.case_number,
                    'status': case.status,
                }
            },
            status=status.HTTP_200_OK
        )

class CandidateBGVCaseDashboardView(APIView):
    permission_classes = [IsCandidate]

    def get(self, request, pk):
        try:
            case = BGVCase.objects.select_related(
                'candidate'
            ).get(pk=pk)
        except BGVCase.DoesNotExist:
            return Response(
                {'detail': 'BGV case not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if case.candidate.user != request.user:
            return Response(
                {
                    'detail':
                    'You do not have access to this BGV case.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        verifications = Verification.objects.filter(
            candidate=case.candidate
        )

        total = verifications.count()

        verified = verifications.filter(
            status=Verification.Status.VERIFIED
        ).count()

        pending = verifications.filter(
            status=Verification.Status.PENDING
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

        verified_percentage = (
            round((verified / total) * 100, 2)
            if total > 0
            else 0
        )

        report = getattr(
            case.candidate,
            'report',
            None
        )

        return Response({
            'case': {
                'id': case.id,
                'case_number': case.case_number,
                'status': case.status,
            },

            'candidate': {
                'id': case.candidate.id,
                'candidate_code':
                    case.candidate.candidate_code,
                'name': (
                    f"{case.candidate.first_name} "
                    f"{case.candidate.last_name}"
                ).strip(),
            },

            'verification_summary': {
                'total': total,
                'verified': verified,
                'pending': pending,
                'in_progress': in_progress,
                'failed': failed,
                'on_hold': on_hold,
                'verified_percentage':
                    verified_percentage,
            },

            'report': {
                'id': report.id if report else None,
                'status':
                    report.status if report else None,
            },
            'verifications': [
                {
                    'id': verification.id,
                    'verification_type': verification.             verification_type,
                    'status': verification.status,
                    'remarks': verification.remarks,
                    'result': verification.result,
                }
                for verification in verifications
            ],
        }, status=status.HTTP_200_OK)
