from django.db import models

class Recommendation(models.Model):
    user = models.ForeignKey(
        'client.User',
        on_delete=models.CASCADE,
        related_name='recommendations'
    )

    # Added according to your requirement
    offer = models.ForeignKey(
        'offers.Offer',
        on_delete=models.CASCADE,
        related_name='recommendations',
        null=True,
        blank=True
    )

    # Why was this recommended?
    match_score = models.FloatField(
        help_text="How well this matches user preferences (0-100)"
    )
    reason = models.TextField(
        blank=True,
        help_text="E.g., 'Matches your preferred star rating and destination'"
    )
    
    # Tracking
    is_viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)
    is_clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)
    is_booked = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Hide outdated recommendations"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'offer')   # ensure 1 recommendation per user-offer pair
        ordering = ['-match_score', '-created_at']
    
    def __str__(self):
        # Safe fallback if offer is null
        offer_title = self.offer.title if self.offer else "No Offer"
        return f"Recommendation: {offer_title} for {self.user.get_full_name()}"
