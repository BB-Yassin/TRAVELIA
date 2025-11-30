from django.contrib import admin
from .models import Destination, Offre, Hebergement

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('nom_destination', 'pays', 'saison')

@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = ('titre', 'prix_par_personne', 'actif')
    list_filter = ('actif',)
    search_fields = ('titre', 'destination',)


@admin.register(Hebergement)
class HebergementAdmin(admin.ModelAdmin):
    list_display = ('nom_hebergement', 'type_hebergement', 'destination', 'etoiles')
