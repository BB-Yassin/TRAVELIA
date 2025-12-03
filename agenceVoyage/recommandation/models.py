from django.db import models
from django.conf import settings

class Recommendation(models.Model):
    RECOMMENDATION_TYPE = [
        ('offer', 'Offre'),
        ('destination', 'Destination'),
        ('hebergement', 'Hébergement'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    
    # Recommandation peut être une offre, destination ou hébergement
    recommendation_type = models.CharField(
        max_length=20,
        choices=RECOMMENDATION_TYPE,
        default='offer'
    )
    
    offer = models.ForeignKey(
        'offreDestination.Offre',
        on_delete=models.CASCADE,
        related_name='recommendations',
        null=True,
        blank=True
    )
    
    destination = models.ForeignKey(
        'offreDestination.Destination',
        on_delete=models.CASCADE,
        related_name='recommendations',
        null=True,
        blank=True
    )
    
    hebergement = models.ForeignKey(
        'offreDestination.Hebergement',
        on_delete=models.CASCADE,
        related_name='recommendations',
        null=True,
        blank=True
    )
    
    # Scoring et raison
    match_score = models.FloatField(
        help_text="Score de correspondance avec les préférences (0-100)"
    )
    
    reason = models.TextField(
        blank=True,
        help_text="Raison de la recommandation"
    )
    
    # Facteurs de recommandation
    preference_match = models.FloatField(default=0, help_text="Score correspondance préférences")
    price_match = models.FloatField(default=0, help_text="Score correspondance prix")
    tier_bonus = models.FloatField(default=0, help_text="Bonus selon le tier")
    popularity_score = models.FloatField(default=0, help_text="Score de popularité")
    
    # Tracking
    is_viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)
    is_clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)
    is_booked = models.BooleanField(default=False)
    booked_at = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-match_score', '-created_at']
        indexes = [
            models.Index(fields=['user', '-match_score']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        item = self.offer or self.destination or self.hebergement
        return f"Recommandation pour {self.user.username} - {item}"


class RecommendationFeedback(models.Model):
    FEEDBACK_CHOICES = [
        ('relevant', 'Pertinent'),
        ('not_relevant', 'Non pertinent'),
        ('already_visited', 'Déjà visité'),
        ('interested', 'Intéressé'),
    ]
    
    recommendation = models.OneToOneField(
        Recommendation,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_CHOICES)
    rating = models.PositiveIntegerField(null=True, blank=True, help_text="Note de 1 à 5")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback pour {self.recommendation} - {self.feedback_type}"
        return f"Recommendation: {offer_title} for {self.user.get_full_name()}"
