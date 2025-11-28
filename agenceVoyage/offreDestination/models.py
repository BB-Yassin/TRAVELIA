from django.db import models

class Destination(models.Model):
    nom_destination = models.CharField(max_length=100)
    pays = models.CharField(max_length=100)
    description = models.TextField()
    saison = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to="destinations/")

    def __str__(self):
        return f"{self.nom_destination} ({self.pays})"


class Offre(models.Model):
    titre = models.CharField(max_length=150)
    description = models.TextField()
    nom_destinations = models.ManyToManyField(Destination, related_name="offres")
    prix_par_personne = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="offres/")
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.titre


class Hebergement(models.Model):
    TYPES = [
        ('hotel', 'Hôtel'),
        ('villa', 'Villa'),
        ('appartement', 'Appartement'),
        ('auberge', 'Auberge'),
        ('resort', 'Resort'),
    ]

    nom_hebergement = models.CharField(max_length=150)
    type_hebergement = models.CharField(max_length=20, choices=TYPES)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name="hebergements")
    
    prix_par_nuit = models.DecimalField(max_digits=10, decimal_places=2)
    etoiles = models.PositiveIntegerField(default=3)
    image = models.ImageField(upload_to="hebergements/", blank=True, null=True)

    offres = models.ManyToManyField(Offre, blank=True, related_name="hebergements")

    def __str__(self):
        return f"{self.nom_hebergement} - {self.destination.nom_destination}"