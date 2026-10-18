from django.conf import settings
from django.db import models

from candidates.models import Candidate


class BGVCase(models.Model):

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        ON_HOLD = 'ON_HOLD', 'On Hold'
        CLOSED = 'CLOSED', 'Closed'

    case_number = models.CharField(
        max_length=30,
        unique=True
    )

    candidate = models.OneToOneField(
        Candidate,
        on_delete=models.CASCADE,
        related_name='bgv_case'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_bgv_cases',
        limit_choices_to={'role': 'VERIFIER'}
    )

    priority = models.CharField(
        max_length=20,
        default='NORMAL'
    )

    remarks = models.TextField(
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_bgv_cases'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.case_number} - {self.candidate.candidate_code}"