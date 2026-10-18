from django.conf import settings
from django.db import models

from candidates.models import Candidate


class Verification(models.Model):

    class VerificationType(models.TextChoices):
        EMPLOYMENT = 'EMPLOYMENT', 'Employment'
        EDUCATION = 'EDUCATION', 'Education'
        ADDRESS = 'ADDRESS', 'Address'
        IDENTITY = 'IDENTITY', 'Identity'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        VERIFIED = 'VERIFIED', 'Verified'
        FAILED = 'FAILED', 'Failed'
        ON_HOLD = 'ON_HOLD', 'On Hold'

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='verifications'
    )

    verification_type = models.CharField(
        max_length=20,
        choices=VerificationType.choices
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_verifications'
    )

    remarks = models.TextField(
        blank=True
    )

    result = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.candidate.candidate_code} - "
            f"{self.verification_type} - "
            f"{self.status}"
        )