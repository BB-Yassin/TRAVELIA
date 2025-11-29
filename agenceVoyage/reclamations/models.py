# reclamations/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class Reclamation(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reclamations'
    )

    reservation = models.ForeignKey(
        'reservation.Reservation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reclamations'
    )

    type_de_reclamation = models.CharField(
        max_length=255,
        verbose_name='Sujet de réclamation'
    )

    description = models.TextField()

    PRIORITY_CHOICES = (
        (1, 'Faible'),
        (2, 'Moyenne'),
        (3, 'Haute'),
    )
    priorite = models.PositiveSmallIntegerField(
        choices=PRIORITY_CHOICES,
        default=3
    )

    STATUS_CHOICES = (
        ('en_progression', 'En progression'),
        ('resolu', 'Résolu'),
        ('ferme', 'Fermé'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='en_progression'
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_resolution = models.DateTimeField(null=True, blank=True)

    def submitter_name(self):
        if self.client:
            return (f"{self.client.first_name} {self.client.last_name}").strip()
        return "Anonyme"

    def __str__(self):
        return f"Réclamation #{self.id} — {self.submitter_name()}"

class ReclamationComment(models.Model):
    reclamation = models.ForeignKey(
        Reclamation,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    description = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire #{self.id}"


