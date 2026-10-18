from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from documents.models import Document
from accounts.permissions import IsAdminOrHR, IsClient, IsVerifier, IsCandidate
from candidates.models import Candidate
from reports.models import Report
from verifications.models import Verification


class AdminHRDashboardView(APIView):
    permission_classes = [IsAdminOrHR]

    def get(self, request):
        total_candidates = Candidate.objects.count()

        candidate_status_summary = {
    'ACTIVE': Candidate.objects.filter(
        status=Candidate.Status.ACTIVE
    ).count(),

    'IN_PROGRESS': Candidate.objects.filter(
        status=Candidate.Status.IN_PROGRESS
    ).count(),

    'COMPLETED': Candidate.objects.filter(
        status=Candidate.Status.COMPLETED
    ).count(),

    'HOLD': Candidate.objects.filter(
        status=Candidate.Status.HOLD
    ).count(),

    'REJECTED': Candidate.objects.filter(
        status=Candidate.Status.REJECTED
    ).count(),
    }
        verification_status_summary = {
    'PENDING': Verification.objects.filter(
        status=Verification.Status.PENDING
    ).count(),

    'IN_PROGRESS': Verification.objects.filter(
        status=Verification.Status.IN_PROGRESS
    ).count(),

    'VERIFIED': Verification.objects.filter(
        status=Verification.Status.VERIFIED
    ).count(),

    'FAILED': Verification.objects.filter(
        status=Verification.Status.FAILED
    ).count(),

    'ON_HOLD': Verification.objects.filter(
        status=Verification.Status.ON_HOLD
    ).count(),
}

        document_status_summary = {
    'PENDING': Document.objects.filter(
        status=Document.Status.PENDING
    ).count(),

    'VERIFIED': Document.objects.filter(
        status=Document.Status.VERIFIED
    ).count(),

    'REJECTED': Document.objects.filter(
        status=Document.Status.REJECTED
    ).count(),
}

        verification_type_summary = {
            'EMPLOYMENT': Verification.objects.filter(
        verification_type=Verification.VerificationType.EMPLOYMENT
        ).count(),

    'EDUCATION': Verification.objects.filter(
        verification_type=Verification.VerificationType.EDUCATION
    ).count(),

    'ADDRESS': Verification.objects.filter(
        verification_type=Verification.VerificationType.ADDRESS
    ).count(),

    'IDENTITY': Verification.objects.filter(
        verification_type=Verification.VerificationType.IDENTITY
    ).count(),
}

        completed_bgv_candidates = Candidate.objects.filter(
           status=Candidate.Status.COMPLETED
        ).count()

        pending_bgv_candidates = Candidate.objects.exclude(
            status=Candidate.Status.COMPLETED
        ).count()

        recent_candidates = Candidate.objects.order_by(
            '-created_at'
        )[:5]

        recent_documents = Document.objects.select_related(
            'candidate'
        ).order_by('-uploaded_at')[:5]

        recent_reports = Report.objects.select_related(
            'candidate'
        ).order_by('-updated_at')[:5]

        pending_verification_queue = Verification.objects.select_related(
            'candidate',
            'assigned_to'
        ).filter(
             status=Verification.Status.PENDING
        ).order_by('-created_at')[:10]

        total_verifications = Verification.objects.count()

        pending_verifications = Verification.objects.filter(
            status=Verification.Status.PENDING
        ).count()

        unassigned_verification_queue = Verification.objects.select_related(
    'candidate'
).filter(
    assigned_to__isnull=True
).order_by('-created_at')[:10]

        unassigned_verifications_count = Verification.objects.filter(
    assigned_to__isnull=True
).count()

        unassigned_document_queue = Document.objects.select_related(
    'candidate'
).filter(
    verification__isnull=True
).order_by('-uploaded_at')[:10]

        unassigned_documents_count = Document.objects.filter(
                verification__isnull=True
            ).count()
        in_progress_verifications = Verification.objects.filter(
            status=Verification.Status.IN_PROGRESS
        ).count()

        verified_verifications = Verification.objects.filter(
            status=Verification.Status.VERIFIED
        ).count()

        failed_verifications = Verification.objects.filter(
            status=Verification.Status.FAILED
        ).count()

        verification_success_rate = 0

        if total_verifications > 0:
           verification_success_rate = round(
               (
                   verified_verifications
                   / total_verifications
                ) * 100,
                2
            )

        report_status_summary = {
           'DRAFT': Report.objects.filter(
               status=Report.Status.DRAFT
            ).count(),

            'FINAL': Report.objects.filter(
                status=Report.Status.FINAL
            ).count(),
        }

        final_reports = Report.objects.filter(
            status=Report.Status.FINAL
        ).count()

        return Response(
            {
                'total_candidates': total_candidates,
                'candidate_status_summary': candidate_status_summary,
                'verification_status_summary': verification_status_summary,
                'document_status_summary': document_status_summary,
                'verification_type_summary': verification_type_summary,
                'bgv_completion_summary': {
                'completed': completed_bgv_candidates,
                'pending': pending_bgv_candidates,
                'total': total_candidates,
                },
                'verification_success_rate': verification_success_rate,
                'report_status_summary': report_status_summary,
                'total_verifications': total_verifications,
                'pending_verifications': pending_verifications,
                'in_progress_verifications': in_progress_verifications,
                'verified_verifications': verified_verifications,
                'failed_verifications': failed_verifications,
                'final_reports': final_reports,
                'recent_candidates' : [
                    {
                        'id' : candidate.id,
                        'candidate_code' : candidate.candidate_code,
                        'first_name' : candidate.first_name,
                        'last_name' : candidate.last_name,
                        'email' : candidate.email,
                        'status' : candidate.status,
                        'created_at' : candidate.created_at,
                    }
                    for candidate in recent_candidates
                ],
                'recent_documents': [
                    {
                        'id': document.id,
                        'candidate_code': document.candidate.candidate_code,
                        'candidate_name': (
                        f"{document.candidate.first_name} "
                        f"{document.candidate.last_name}"
                    ),
                        'document_type': document.document_type,
                        'document_name': document.document_name,
                        'status': document.status,
                        'uploaded_at': document.uploaded_at,
                    }
                    for document in recent_documents
                ],
'recent_reports': [
    {
        'id': report.id,
        'candidate_id': report.candidate.id,
        'candidate_code': report.candidate.candidate_code,
        'candidate_name': (
            f"{report.candidate.first_name} "
            f"{report.candidate.last_name}"
        ),
        'status': report.status,
        'generated_at': report.generated_at,
        'updated_at': report.updated_at,
    }
    for report in recent_reports
],
'pending_verification_queue': [
    {
        'id': verification.id,
        'candidate_id': verification.candidate.id,
        'candidate_code': verification.candidate.candidate_code,
        'candidate_name': (
            f"{verification.candidate.first_name} "
            f"{verification.candidate.last_name}"
        ),
        'verification_type': verification.verification_type,
        'status': verification.status,
        'assigned_to': (
            verification.assigned_to.username
            if verification.assigned_to
            else None
        ),
        'created_at': verification.created_at,
    }
    for verification in pending_verification_queue
],

'unassigned_verification_queue': [
    {
        'id': verification.id,
        'candidate_id': verification.candidate.id,
        'candidate_code': verification.candidate.candidate_code,
        'candidate_name': (
            f"{verification.candidate.first_name} "
            f"{verification.candidate.last_name}"
        ),
        'verification_type': verification.verification_type,
        'status': verification.status,
        'created_at': verification.created_at,
    }
    for verification in unassigned_verification_queue
],

'unassigned_verifications_count': unassigned_verifications_count,
'unassigned_documents_count': unassigned_documents_count,

'unassigned_document_queue': [
    {
        'id': document.id,
        'candidate_id': document.candidate.id,
        'candidate_code': document.candidate.candidate_code,
        'candidate_name': (
            f"{document.candidate.first_name} "
            f"{document.candidate.last_name}"
        ),
        'document_type': document.document_type,
        'document_name': document.document_name,
        'status': document.status,
        'uploaded_at': document.uploaded_at,
    }
    for document in unassigned_document_queue
],
            },
            status=status.HTTP_200_OK
        )


class ClientDashboardView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        client = request.user

        my_candidates = Candidate.objects.filter(
            client=client
        )
        recent_candidates = my_candidates.order_by('-created_at')[:5]

        total_candidates = my_candidates.count()

        total_verifications = Verification.objects.filter(
            candidate__client=client
        ).count()

        pending_verifications = Verification.objects.filter(
            candidate__client=client,
            status=Verification.Status.PENDING
        ).count()

        in_progress_verifications = Verification.objects.filter(
            candidate__client=client,
            status=Verification.Status.IN_PROGRESS
        ).count()

        verified_verifications = Verification.objects.filter(
            candidate__client=client,
            status=Verification.Status.VERIFIED
        ).count()

        failed_verifications = Verification.objects.filter(
            candidate__client=client,
            status=Verification.Status.FAILED
        ).count()

        final_reports = Report.objects.filter(
            candidate__client=client,
            status=Report.Status.FINAL
        ).count()

        return Response(
            {
                'total_candidates': total_candidates,
                'total_verifications': total_verifications,
                'pending_verifications': pending_verifications,
                'in_progress_verifications': in_progress_verifications,
                'verified_verifications': verified_verifications,
                'failed_verifications': failed_verifications,
                'final_reports': final_reports,
                'recent_candidates': [
                    {
                        'id': candidate.id,
                        'candidate_code': candidate.                candidate_code,
                        'first_name': candidate.first_name,
                        'last_name': candidate.last_name,
                        'email': candidate.email,
                        'status': candidate.status,
                        'created_at': candidate.created_at,
                    }
                    for candidate in recent_candidates
                ],
            },
            status=status.HTTP_200_OK
        )

class VerifierDashboardView(APIView):
    permission_classes = [IsVerifier]

    def get(self, request):
        verifier = request.user

        my_verifications = Verification.objects.filter(
            assigned_to=verifier
        )
        recent_verifications = my_verifications.    select_related(
    'candidate'
).order_by('-updated_at')[:5]

        total_assigned = my_verifications.count()

        pending_verifications = my_verifications.filter(
            status=Verification.Status.PENDING
        ).count()

        in_progress_verifications = my_verifications.filter(
            status=Verification.Status.IN_PROGRESS
        ).count()

        verified_verifications = my_verifications.filter(
            status=Verification.Status.VERIFIED
        ).count()

        failed_verifications = my_verifications.filter(
            status=Verification.Status.FAILED
        ).count()

        on_hold_verifications = my_verifications.filter(
            status=Verification.Status.ON_HOLD
        ).count()

        return Response(
            {
                'total_assigned': total_assigned,
                'pending_verifications': pending_verifications,
                'in_progress_verifications': in_progress_verifications,
                'verified_verifications': verified_verifications,
                'failed_verifications': failed_verifications,
                'on_hold_verifications': on_hold_verifications,
                'recent_verifications': [
                     {
                         'id': verification.id,
                         'candidate_code': verification.candidate.                 candidate_code,
                         'candidate_name': (
                             f"{verification.candidate.first_name}                  "
                             f"{verification.candidate.last_name}"
                         ),
                         'verification_type': verification.                 verification_type,
                         'status': verification.status,
                         'updated_at': verification.updated_at,
                     }
                     for verification in recent_verifications
                 ],
            },
            status=status.HTTP_200_OK
        )

class CandidateDashboardView(APIView):
    permission_classes = [IsCandidate]

    def get(self, request):
        candidate = Candidate.objects.filter(
            user=request.user
        ).first()

        if not candidate:
            return Response(
                {
                    'detail': 'Candidate profile not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        my_verifications = Verification.objects.filter(
            candidate=candidate
        )

        total_documents = candidate.documents.count()
        recent_documents = Document.objects.filter(candidate=candidate).order_by('-uploaded_at')[:5]

        total_verifications = my_verifications.count()

        pending_verifications = my_verifications.filter(
            status=Verification.Status.PENDING
        ).count()

        in_progress_verifications = my_verifications.filter(
            status=Verification.Status.IN_PROGRESS
        ).count()

        verified_verifications = my_verifications.filter(
            status=Verification.Status.VERIFIED
        ).count()

        failed_verifications = my_verifications.filter(
            status=Verification.Status.FAILED
        ).count()

        if failed_verifications > 0:
            overall_status = 'FAILED'
        elif total_verifications > 0 and (
            verified_verifications == total_verifications
        ):
            overall_status = 'VERIFIED'
        elif in_progress_verifications > 0:
            overall_status = 'IN_PROGRESS'
        elif pending_verifications > 0:
            overall_status = 'PENDING'
        else:
            overall_status = 'NOT_STARTED'

        return Response(
            {
                'candidate': {
                    'id': candidate.id,
                    'candidate_code': candidate.candidate_code,
                    'first_name': candidate.first_name,
                    'last_name': candidate.last_name,
                    'email': candidate.email,
                    'phone': candidate.phone,
                },
                'total_documents': total_documents,
                'total_verifications': total_verifications,
                'pending_verifications': pending_verifications,
                'in_progress_verifications': in_progress_verifications,
                'verified_verifications': verified_verifications,
                'failed_verifications': failed_verifications,
                'overall_status': overall_status,
                'recent_documents' : [
                    {
                        'id': document.id,
                        'document_type' : document.document_type,
                        'document_name': document.document_name,
                        'status': document.status,
                        'uploaded_at' : document.uploaded_at,
                    }
                    for document in recent_documents
                ],
            },
            status=status.HTTP_200_OK
        )

class RecentVerificationActivityView(APIView):
    permission_classes = [IsAdminOrHR]

    def get(self, request):
        recent_verifications = Verification.objects.select_related(
            'candidate',
            'assigned_to'
        ).order_by('-updated_at')[:10]

        data = []

        for verification in recent_verifications:
            data.append({
                'id': verification.id,
                'candidate_id': verification.candidate.id,
                'candidate_code': verification.candidate.candidate_code,
                'candidate_name': (
                    f"{verification.candidate.first_name} "
                    f"{verification.candidate.last_name}"
                ),
                'verification_type': verification.verification_type,
                'status': verification.status,
                'assigned_to': (
                    verification.assigned_to.username
                    if verification.assigned_to
                    else None
                ),
                'updated_at': verification.updated_at,
            })

        return Response(
            data,
            status=status.HTTP_200_OK
        )