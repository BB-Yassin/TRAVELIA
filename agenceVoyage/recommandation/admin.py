from django.contrib import admin
from .models import Recommendation, RecommendationFeedback


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'recommendation_type', 'match_score', 'is_viewed', 'is_clicked', 'is_booked', 'created_at']
    list_filter = ['recommendation_type', 'is_viewed', 'is_booked', 'created_at']
    search_fields = ['user__username', 'offer__titre', 'destination__nom_destination']
    readonly_fields = ['created_at', 'updated_at', 'viewed_at', 'clicked_at', 'booked_at']
    
    fieldsets = (
        ('Utilisateur', {'fields': ['user']}),
        ('Type et contenu', {'fields': ['recommendation_type', 'offer', 'destination', 'hebergement']}),
        ('Scoring', {'fields': ['match_score', 'preference_match', 'price_match', 'tier_bonus', 'popularity_score']}),
        ('Raison', {'fields': ['reason']}),
        ('Tracking', {'fields': ['is_viewed', 'viewed_at', 'is_clicked', 'clicked_at', 'is_booked', 'booked_at']}),
        ('Status', {'fields': ['is_active', 'created_at', 'updated_at']}),
    )


@admin.register(RecommendationFeedback)
class RecommendationFeedbackAdmin(admin.ModelAdmin):
    list_display = ['recommendation', 'feedback_type', 'rating', 'created_at']
    list_filter = ['feedback_type', 'rating', 'created_at']
    search_fields = ['recommendation__user__username', 'comment']
    readonly_fields = ['created_at']
