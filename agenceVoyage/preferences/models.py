from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class TravelClass(models.TextChoices):
    ECONOMY = 'ECONOMY', _('Economy')
    BUSINESS = 'BUSINESS', _('Business')
    FIRST_CLASS = 'FIRST_CLASS', _('First Class')

class MealPreference(models.TextChoices):
    VEGETARIAN = 'VEGETARIAN', _('Vegetarian')
    NON_VEGETARIAN = 'NON_VEGETARIAN', _('Non-Vegetarian')
    VEGAN = 'VEGAN', _('Vegan')

class SeatPreference(models.TextChoices):
    AISLE = 'AISLE', _('Aisle')
    WINDOW = 'WINDOW', _('Window')
    MIDDLE = 'MIDDLE', _('Middle')

class PriceRange(models.TextChoices):
    BUDGET = 'BUDGET', _('Budget')
    STANDARD = 'STANDARD', _('Standard')
    PREMIUM = 'PREMIUM', _('Premium')

class Preference(models.Model):  # PascalCase for class names
    user = models.OneToOneField(  # OneToOne since each user has one preference
        'client.User', 
        on_delete=models.CASCADE,
        related_name='preference'
    )
    travel_class = models.CharField(  # snake_case for field names
        max_length=20,
        choices=TravelClass.choices,
        default=TravelClass.ECONOMY
    )
    meal_preference = models.CharField(
        max_length=20,
        choices=MealPreference.choices,
        default=MealPreference.NON_VEGETARIAN
    )
    seat_preference = models.CharField(
        max_length=20,
        choices=SeatPreference.choices,
        default=SeatPreference.AISLE
    )
    price_range = models.CharField(
        max_length=20,
        choices=PriceRange.choices,
        default=PriceRange.STANDARD
    )
    minimum_star_rating = models.PositiveIntegerField(  # Fixed typo
        validators=[
            MinValueValidator(1, message="Star rating must be at least 1"),
            MaxValueValidator(5, message="Star rating cannot exceed 5")
        ],
        default=3,
        help_text="Preferred minimum star rating (1-5)"
    )
    special_notes = models.TextField(
        blank=True,
        help_text="Any other recurring special requests or preferences"
    )
    created_at = models.DateTimeField(auto_now_add=True)  # snake_case
    updated_at = models.DateTimeField(auto_now=True)  # Renamed for clarity
    
    def __str__(self):
        return f"Preferences for {self.user.get_full_name()}"
    
    class Meta:
        verbose_name = _('User Preference')
        verbose_name_plural = _('User Preferences')