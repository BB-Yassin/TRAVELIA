from rest_framework import serializers
from .models import Recommendation, RecommendationFeedback
from offreDestination.models import Offre, Destination, Hebergement


class OffreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offre
        fields = ['id', 'titre', 'description', 'prix_par_personne']


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ['id', 'nom_destination', 'pays', 'description']


class HebergementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hebergement
        fields = ['id', 'nom_hebergement', 'type_hebergement', 'prix_par_nuit', 'etoiles']


class RecommendationFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationFeedback
        fields = ['feedback_type', 'rating', 'comment', 'created_at']


class RecommendationSerializer(serializers.ModelSerializer):
    offer = OffreSerializer(read_only=True)
    destination = DestinationSerializer(read_only=True)
    hebergement = HebergementSerializer(read_only=True)
    feedback = RecommendationFeedbackSerializer(read_only=True)
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'recommendation_type', 'offer', 'destination', 'hebergement',
            'match_score', 'reason', 'preference_match', 'price_match',
            'tier_bonus', 'popularity_score', 'is_viewed', 'is_clicked',
            'is_booked', 'feedback', 'created_at'
        ]
