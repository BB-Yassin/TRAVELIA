from django.urls import path
from . import views

app_name = 'offreDestination'

urlpatterns = [
    path("", views.liste_offres, name="offers-list"),
    path("offres/", views.liste_offres, name="liste_offres"),
    path("offres/<int:pk>/", views.offre_detail, name="offre_detail"),
    path("destinations/", views.liste_destinations, name="destinations"),
    path("destinations/<int:pk>/", views.destination_detail, name="destination_detail"),
    path("hebergements/", views.liste_hebergements, name="liste_hebergements"),
    path("hebergements/<int:pk>/", views.hebergement_detail, name="hebergement_detail"),

]
