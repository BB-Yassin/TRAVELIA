# feedback/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from simple_history.models import HistoricalRecords

class Feedback(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='feedbacks',
        default=1
    )
    offer = models.ForeignKey(
        'offreDestination.Offre',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='feedbacks',
        verbose_name='offre',
        default=1
    )
    note_service = models.PositiveSmallIntegerField(verbose_name="Qualité Service (0-5)", default=0)
    note_hebergement = models.PositiveSmallIntegerField(verbose_name="Hébergement (0-5)", default=0)
    note_valeur = models.PositiveSmallIntegerField(verbose_name="Rapport Qualité/Prix (0-5)", default=0)
    
    history = HistoricalRecords()
    date_soumission = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    attachement = models.FileField(upload_to='feedback_attachments/', null=True, blank=True)

    def submitter_name(self):
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}"
        return "Anonyme"

    def __str__(self):
        return f"Feedback #{self.id} by {self.submitter_name()}"
