from django.db import models
from candidates.models import Candidate


class Report(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        FINAL = 'FINAL', 'Final'

    candidate = models.OneToOneField(
        Candidate,
        on_delete=models.CASCADE,
        related_name='final_report'
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )

    summary = models.TextField(
        blank=True
    )

    generated_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.candidate.candidate_code} - Report"