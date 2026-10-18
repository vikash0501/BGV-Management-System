from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class AuditLog(models.Model):

    class Action(models.TextChoices):
        CASE_CREATED = 'CASE_CREATED', 'Case Created'
        CASE_ASSIGNED = 'CASE_ASSIGNED', 'Case Assigned'
        CASE_PROCESSED = 'CASE_PROCESSED', 'Case Processed'
        VERIFICATION_CREATED = 'VERIFICATION_CREATED', 'Verification Created'
        VERIFICATION_ASSIGNED = 'VERIFICATION_ASSIGNED', 'Verification Assigned'
        VERIFICATION_PROCESSED = 'VERIFICATION_PROCESSED', 'Verification Processed'
        DOCUMENT_UPLOADED = 'DOCUMENT_UPLOADED', 'Document Uploaded'
        DOCUMENT_VERIFIED = 'DOCUMENT_VERIFIED', 'Document Verified'
        REPORT_GENERATED = 'REPORT_GENERATED', 'Report Generated'
        CASE_CLOSED = 'CASE_CLOSED', 'Case Closed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    case = models.ForeignKey(
        'cases.BGVCase',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    action = models.CharField(
        max_length=50,
        choices=Action.choices
    )

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.action} - Case {self.case_id}"