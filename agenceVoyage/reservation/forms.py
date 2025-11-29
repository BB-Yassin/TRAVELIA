from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['nb_personnes', 'client', 'offre', 'mode_paiement']
        widgets = {
            'nb_personnes': forms.NumberInput(attrs={'min': 1}),
            'mode_paiement': forms.Select(),  
        }
