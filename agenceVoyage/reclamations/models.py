from django.db import models
from django.conf import settings
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Reclamation(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reclamations',
        null=False,
        blank=False,
    )

    reservation = models.ForeignKey(
        'reservation.Reservation',   
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
        default=1
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
    
    # SLA Fields
    sla_deadline = models.DateTimeField(null=True, blank=True, verbose_name="Date limite (SLA)")
    breach_flag = models.BooleanField(default=False, verbose_name="SLA dépassé ?")
    
    history = HistoricalRecords()

    def submitter_name(self):
        if self.client:
            name = f"{self.client.first_name} {self.client.last_name}".strip()
            return name or self.client.get_username()
        return "Anonyme"

    def __str__(self):
        return f"Réclamation #{self.id} — {self.submitter_name()}"

    def save(self, *args, **kwargs):
        # 1. Calculate SLA deadline if not set
        if not self.sla_deadline:
            # Low=72h, Medium=48h, High=24h
            hours_map = {1: 72, 2: 48, 3: 24}
            hours = hours_map.get(self.priorite, 48)
            # If it's a new object, use current time, else use creation time if available
            base_time = self.date_creation if self.date_creation else timezone.now()
            self.sla_deadline = base_time + timezone.timedelta(hours=hours)

        # 2. Check for SLA Breach
        # If not resolved/closed and deadline passed
        if self.status == 'en_progression' and self.sla_deadline:
            if timezone.now() > self.sla_deadline:
                self.breach_flag = True
            else:
                self.breach_flag = False
        elif self.status in ('resolu', 'ferme'):
            # If resolved, we might want to keep the flag if it WAS breached, 
            # or check if it was resolved AFTER deadline.
            # Here, let's check if resolution date > deadline
            if self.date_resolution and self.sla_deadline and self.date_resolution > self.sla_deadline:
                self.breach_flag = True
            else:
                # If resolved on time, clear flag? Or keep history? 
                # Let's say if resolved on time, flag is False.
                self.breach_flag = False

        # 3. Handle Status Changes (existing logic)
        if self.pk:
            try:
                old = Reclamation.objects.get(pk=self.pk)
                if self.status in ('resolu', 'ferme') and old.status != self.status:
                    if not self.date_resolution:
                        self.date_resolution = timezone.now()
                if self.status == 'en_progression' and old.status != 'en_progression':
                    self.date_resolution = None
            except Reclamation.DoesNotExist:
                pass # Should not happen if pk exists
        else:
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
