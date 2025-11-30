from django.contrib import admin
from .models import Reservation
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id_reservation', 'client', 'offre', 'nb_personnes', 'prix_total', 'mode_paiement', 'date_reservation')
    list_filter = ('mode_paiement', 'date_reservation')
    search_fields = ('client__username', 'client__first_name', 'client__last_name', 'offre__titre')
    ordering = ('-date_reservation',)
