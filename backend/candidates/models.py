from django.conf import settings
from django.db import models


class Candidate(models.Model):

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        HOLD = 'HOLD', 'On Hold'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='candidate_profile'
    )

    candidate_code = models.CharField(
        max_length=30,
        unique=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100,
        blank=True
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=15
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        blank=True
    )

    pincode = models.CharField(
        max_length=10,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_candidates'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
    client = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='client_candidates',
    limit_choices_to={'role': 'CLIENT'}
)

    def save(self, *args, **kwargs):
        if not self.candidate_code:
            last_candidate = Candidate.objects.order_by('-id').first()

            if last_candidate:
                last_id = last_candidate.id + 1
            else:
                last_id = 1

            self.candidate_code = f"BGV-CAND-{last_id:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.candidate_code} - {self.first_name} {self.last_name}"