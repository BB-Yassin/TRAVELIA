from django.db import models
from django.conf import settings


class Reservation(models.Model):
    id_reservation = models.AutoField(primary_key=True)
    date_reservation = models.DateTimeField(auto_now_add=True)
    prix_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    nb_personnes = models.PositiveIntegerField()

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    offre = models.ForeignKey('offreDestination.Offre', on_delete=models.CASCADE)

    mode_paiement = models.CharField(max_length=20, null=True, blank=True)

    def save(self, *args, **kwargs):
        # calculate total price before saving
        if self.offre and self.nb_personnes:
            self.prix_total = self.offre.prix_par_personne * self.nb_personnes

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client.first_name} {self.client.last_name} - {self.date_reservation}"
