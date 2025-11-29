from django.db import models
from django.conf import settings
from django.utils import timezone


class Reclamation(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reclamations',
        null=False,
        blank=False,
    )

    reservation = models.ForeignKey(
        'reservation.Reservation',   # Make sure app name is correct
        on_delete=models.CASCADE,
        related_name='reclamations',
        null=False,
        blank=False,
    )

    type_de_reclamation = models.CharField(
        max_length=255,
        verbose_name='Sujet de réclamation',
        null=False,
        blank=False,
    )

    description = models.TextField(
        null=False,
        blank=False,
    )

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
            name = f"{self.client.first_name} {self.client.last_name}".strip()
            return name or self.client.get_username()
        return "Anonyme"

    def __str__(self):
        return f"Réclamation #{self.id} — {self.submitter_name()}"

    def save(self, *args, **kwargs):
        # Object exists already → check status changes
        if self.pk:
            old = Reclamation.objects.get(pk=self.pk)

            # Status changed to resolved or closed
            if self.status in ('resolu', 'ferme') and old.status != self.status:
                if not self.date_resolution:
                    self.date_resolution = timezone.now()

            # Status changed back to « en progression »
            if self.status == 'en_progression' and old.status != 'en_progression':
                self.date_resolution = None

        else:
            # New object created already resolved/closed → set resolution date now
            if self.status in ('resolu', 'ferme'):
                self.date_resolution = timezone.now()

        super().save(*args, **kwargs)


class ReclamationComment(models.Model):
    reclamation = models.ForeignKey(
        Reclamation,
        on_delete=models.CASCADE,
        related_name='comments',
        null=False,
        blank=False,
    )

    # Optional: user can be null (anonymous or admin)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='reclamation_comments'
    )

    description = models.TextField(
        null=False,
        blank=False
    )

    date_added = models.DateTimeField(auto_now_add=True)

    def submitter_name(self):
        if self.user:
            name = f"{self.user.first_name} {self.user.last_name}".strip()
            return name or self.user.get_username()
        return "Anonyme"

    def __str__(self):
        return f"Commentaire #{self.id} — {self.submitter_name()}"
