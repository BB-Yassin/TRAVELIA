from django.urls import path
from .views import ReservationCreateView, ReservationListView, ReservationUpdateView, ReservationDeleteView

urlpatterns = [
    # Création d'une réservation pour une offre spécifique
    path('creer/<int:offre_id>/', ReservationCreateView.as_view(), name='creer_reservation'),

    # Liste des réservations
    path('listeR/', ReservationListView.as_view(), name='liste_reservations'),

    # Modifier une réservation
    path('modifier/<int:pk>/', ReservationUpdateView.as_view(), name='modifier_reservation'),

    # Supprimer une réservation
    path('supprimer/<int:pk>/', ReservationDeleteView.as_view(), name='supprimer_reservation'),
]
