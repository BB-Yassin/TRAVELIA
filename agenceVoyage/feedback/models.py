# feedback/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class Feedback(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks'
    )
    offer = models.ForeignKey(
        'offreDestination.Offre',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='feedbacks',
        verbose_name='offre'
    )
    note = models.PositiveSmallIntegerField(null=True, blank=True)  # rating 1..5
    date_soumission = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    attachement = models.FileField(upload_to='feedback_attachments/', null=True, blank=True)

    def submitter_name(self):
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}"
        return "Anonyme"

    def __str__(self):
        return f"Feedback #{self.id} by {self.submitter_name()}"
