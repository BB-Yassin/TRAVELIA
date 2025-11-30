from django.contrib import admin
from .models import Destination, Offre, Hebergement


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('nom_destination', 'pays', 'saison')
    search_fields = ('nom_destination', 'pays')


@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = ('titre', 'prix_par_personne', 'actif')
    search_fields = ('titre',)
    filter_horizontal = ('nom_destinations',)


@admin.register(Hebergement)
class HebergementAdmin(admin.ModelAdmin):
    list_display = ('nom_hebergement', 'type_hebergement', 'destination', 'prix_par_nuit', 'etoiles')
    search_fields = ('nom_hebergement', 'destination__nom_destination')
    list_filter = ('type_hebergement', 'destination', 'etoiles')
    filter_horizontal = ('offres',)
