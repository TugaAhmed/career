# applications/models.py
import uuid
from django.db import models
from django.conf import settings
from jobs.models import Job

class Application(models.Model):
    STATUS_APPLIED = "Applied"
    STATUS_REVIEWED = "Reviewed"
    STATUS_INTERVIEW = "Interview"
    STATUS_REJECTED = "Rejected"
    STATUS_HIRED = "Hired"
    STATUS_CHOICES = [
        (STATUS_APPLIED, "Applied"),
        (STATUS_REVIEWED, "Reviewed"),
        (STATUS_INTERVIEW, "Interview"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_HIRED, "Hired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    resume_link = models.URLField()
    cover_letter = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_APPLIED)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('applicant', 'job')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant.email} -> {self.job.title}"
