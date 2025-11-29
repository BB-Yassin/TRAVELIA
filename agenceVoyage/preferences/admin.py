from django.contrib import admin
from .models import Preference

@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'travel_class', 'meal_preference', 'seat_preference', 'price_range', 'minimum_star_rating')
