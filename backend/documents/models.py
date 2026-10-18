from django.conf import settings
from django.db import models

from candidates.models import Candidate
from verifications.models import Verification


class Document(models.Model):

    class DocumentType(models.TextChoices):
        IDENTITY = 'IDENTITY', 'Identity Proof'
        EDUCATION = 'EDUCATION', 'Education Certificate'
        EMPLOYMENT = 'EMPLOYMENT', 'Employment Document'
        ADDRESS = 'ADDRESS', 'Address Proof'
        OTHER = 'OTHER', 'Other'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        VERIFIED = 'VERIFIED', 'Verified'
        REJECTED = 'REJECTED', 'Rejected'

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    verification = models.ForeignKey(
        Verification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )

    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices
    )

    document_name = models.CharField(
        max_length=255
    )

    file = models.FileField(
        upload_to='documents/'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.candidate.candidate_code} - "
            f"{self.document_type} - "
            f"{self.document_name}"
        )