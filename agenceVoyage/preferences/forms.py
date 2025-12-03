from django import forms
from .models import Preference


class PreferenceForm(forms.ModelForm):
    class Meta:
        model = Preference
        fields = [
            'travel_class',
            'meal_preference',
            'seat_preference',
            'price_range',
        ]
        widgets = {
            'travel_class': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select travel class'
            }),
            'meal_preference': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select meal preference'
            }),
            'seat_preference': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select seat preference'
            }),
            'price_range': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select price range'
            }),
        }
        labels = {
            'travel_class': 'Preferred Travel Class',
            'meal_preference': 'Meal Preference',
            'seat_preference': 'Seat Preference',
            'price_range': 'Price Range',
        }

