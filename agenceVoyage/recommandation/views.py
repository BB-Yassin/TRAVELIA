from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Avg, Count, DecimalField
from django.db.models.functions import Cast
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Recommendation, RecommendationFeedback
from offreDestination.models import Offre, Destination, Hebergement
from preferences.models import Preference, PriceRange
from programmeFidilite.models import LoyaltyProgram
from .serializers import RecommendationSerializer, RecommendationFeedbackSerializer


class RecommendationEngine:
    """Moteur de recommandation basé sur les préférences et le tier"""
    
    def __init__(self, user):
        self.user = user
        self.preferences = getattr(user, 'preference', None)
        self.loyalty = getattr(user, 'loyalty_program', None)
    
    def calculate_offer_score(self, offer):
        """Calcule le score de correspondance pour une offre"""
        score = 0.0
        reasons = []
        
        # 1. Score de préférences (40%)
        preference_score = self._calculate_preference_score(offer)
        score += preference_score * 0.4
        
        # 2. Score de prix (30%)
        price_score = self._calculate_price_score(offer)
        score += price_score * 0.3
        
        # 3. Bonus tier (20%)
        tier_bonus = self._calculate_tier_bonus()
        score += tier_bonus * 0.2
        
        # 4. Popularité (10%)
        popularity = self._calculate_popularity(offer)
        score += popularity * 0.1
        
        return min(score, 100), self._generate_reason(offer, preference_score, price_score, tier_bonus)
    
    def calculate_destination_score(self, destination):
        """Calcule le score pour une destination"""
        score = 0.0
        
        # Basé sur les hébergements disponibles
        hebergements = destination.hebergements.all()
        if hebergements.exists():
            avg_stars = hebergements.aggregate(Avg('etoiles'))['etoiles__avg'] or 3
            # Score basé sur les étoiles
            score += (avg_stars / 5) * 50
        
        # Popularité
        avg_reservations = hebergements.aggregate(
            Count('reservations')
        )['reservations__count'] or 0
        score += min(avg_reservations / 10, 50)
        
        return min(score, 100)
    
    def calculate_hebergement_score(self, hebergement):
        """Calcule le score pour un hébergement"""
        score = 0.0
        
        # Basé sur les étoiles (50%)
        stars_score = (hebergement.etoiles / 5) * 100
        score += stars_score * 0.5
        
        # Prix (30%)
        price_score = self._calculate_accommodation_price_score(hebergement)
        score += price_score * 0.3
        
        # Bonus tier (20%)
        tier_bonus = self._calculate_tier_bonus()
        score += tier_bonus * 0.2
        
        return min(score, 100)
    
    def _calculate_preference_score(self, offer):
        """Score basé sur les préférences utilisateur"""
        if not self.preferences:
            return 50.0
        
        score = 50.0
        
        # Destinations préférées
        destinations = offer.nom_destinations.all()
        if destinations.exists():
            # Bonus si dans les destinations de l'offre
            score += 25
        
        return min(score, 100)
    
    def _calculate_price_score(self, offer):
        """Score basé sur le prix et la plage de prix préférée"""
        if not self.preferences:
            return 50.0
        
        price = float(offer.prix_par_personne)
        
        # Plages de prix définies
        price_ranges = {
            PriceRange.BUDGET: (0, 500),
            PriceRange.STANDARD: (500, 1500),
            PriceRange.PREMIUM: (1500, 10000),
        }
        
        min_price, max_price = price_ranges.get(
            self.preferences.price_range,
            (0, 10000)
        )
        
        # Score basé sur la plage de prix
        if min_price <= price <= max_price:
            return 100.0
        elif price < min_price:
            return max(0, 100 - (min_price - price) / 10)
        else:
            return max(0, 100 - (price - max_price) / 10)
    
    def _calculate_accommodation_price_score(self, hebergement):
        """Score pour l'hébergement basé sur le prix"""
        if not self.preferences:
            return 50.0
        
        price = float(hebergement.prix_par_nuit)
        
        price_ranges = {
            PriceRange.BUDGET: (0, 100),
            PriceRange.STANDARD: (100, 300),
            PriceRange.PREMIUM: (300, 1000),
        }
        
        min_price, max_price = price_ranges.get(
            self.preferences.price_range,
            (0, 1000)
        )
        
        if min_price <= price <= max_price:
            return 100.0
        elif price < min_price:
            return max(0, 100 - (min_price - price) / 2)
        else:
            return max(0, 100 - (price - max_price) / 2)
    
    def _calculate_tier_bonus(self):
        """Bonus basé sur le tier de fidélité"""
        if not self.loyalty or not self.loyalty.tier:
            return 0
        
        tier_bonuses = {
            'BRONZE': 5,
            'SILVER': 15,
            'GOLD': 25,
            'PLATINUM': 35,
        }
        
        return tier_bonuses.get(self.loyalty.tier, 5)
    
    def _calculate_popularity(self, offer):
        """Calcule la popularité d'une offre"""
        # Basé sur le nombre de réservations
        reservation_count = offer.reservations.count() if hasattr(offer, 'reservations') else 0
        rating = min(reservation_count / 5, 100)
        
        # Bonus si l'offre a des hébergements 5 étoiles
        hebergements = offer.hebergements.all()
        if hebergements.filter(etoiles=5).exists():
            rating += 20
        
        return min(rating, 100)
    
    def _generate_reason(self, offer, pref_score, price_score, tier_bonus):
        """Génère une raison pour la recommandation"""
        reasons = []
        
        if pref_score > 70:
            reasons.append("Correspond à vos préférences")
        
        if price_score > 80:
            reasons.append("Prix avantageux pour votre gamme")
        
        if tier_bonus > 0:
            reasons.append(f"Avantage spécial {self.loyalty.tier if self.loyalty else 'Bronze'}")
        
        # Bonus hébergement 5 étoiles
        hebergements = offer.hebergements.all()
        if hebergements.filter(etoiles=5).exists():
            reasons.append("Hébergement 5 étoiles disponible")
        
        return " • ".join(reasons) if reasons else "Recommandé pour vous"
    
    def generate_recommendations(self, limit=10):
        """Génère les recommandations"""
        recommendations = []
        
        # Récupérer les offres actives
        offers = Offre.objects.filter(actif=True)
        
        for offer in offers:
            score, reason = self.calculate_offer_score(offer)
            if score > 40:  # Seuil minimum
                recommendations.append({
                    'type': 'offer',
                    'item': offer,
                    'score': score,
                    'reason': reason,
                    'preference_match': score * 0.4,
                    'price_match': score * 0.3,
                    'tier_bonus': self._calculate_tier_bonus(),
                    'popularity': score * 0.1,
                })
        
        # Trier par score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:limit]


@login_required
@require_http_methods(["GET"])
def get_recommendations(request):
    """Récupère les recommandations pour l'utilisateur"""
    engine = RecommendationEngine(request.user)
    recommendations = engine.generate_recommendations(limit=10)
    
    # Sauvegarder les recommandations
    for rec in recommendations:
        Recommendation.objects.update_or_create(
            user=request.user,
            offer=rec['item'],
            recommendation_type='offer',
            defaults={
                'match_score': rec['score'],
                'reason': rec['reason'],
                'preference_match': rec['preference_match'],
                'price_match': rec['price_match'],
                'tier_bonus': rec['tier_bonus'],
                'popularity_score': rec['popularity'],
                'is_active': True,
            }
        )
    
    context = {
        'recommendations': recommendations,
        'user': request.user,
    }
    
    return render(request, 'recommandation/recommendations.html', context)


@login_required
@require_http_methods(["GET"])
def recommendation_detail(request, recommendation_id):
    """Détail d'une recommandation"""
    recommendation = get_object_or_404(
        Recommendation,
        id=recommendation_id,
        user=request.user
    )
    
    # Marquer comme vue
    if not recommendation.is_viewed:
        recommendation.is_viewed = True
        recommendation.viewed_at = timezone.now()
        recommendation.save()
    
    context = {
        'recommendation': recommendation,
    }
    
    return render(request, 'recommandation/recommendation_detail.html', context)


# ============== API VIEWS (REST Framework) ==============

class RecommendationViewSet(viewsets.ViewSet):
    """API pour les recommandations"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_recommendations(self, request):
        """Mes recommandations personnalisées"""
        engine = RecommendationEngine(request.user)
        recommendations = engine.generate_recommendations(limit=20)
        
        # Sauvegarder
        for rec in recommendations:
            Recommendation.objects.update_or_create(
                user=request.user,
                offer=rec['item'],
                recommendation_type='offer',
                defaults={
                    'match_score': rec['score'],
                    'reason': rec['reason'],
                    'preference_match': rec['preference_match'],
                    'price_match': rec['price_match'],
                    'tier_bonus': rec['tier_bonus'],
                    'popularity_score': rec['popularity'],
                }
            )
        
        # Récupérer depuis BD
        recs = Recommendation.objects.filter(
            user=request.user,
            is_active=True
        )[:20]
        
        serializer = RecommendationSerializer(recs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_destinations(self, request):
        """Top destinations recommandées"""
        engine = RecommendationEngine(request.user)
        
        destinations = []
        for dest in Destination.objects.all():
            score = engine.calculate_destination_score(dest)
            if score > 40:
                destinations.append({
                    'destination': dest,
                    'score': score,
                })
        
        destinations.sort(key=lambda x: x['score'], reverse=True)
        
        return Response([
            {
                'id': d['destination'].id,
                'nom': d['destination'].nom_destination,
                'pays': d['destination'].pays,
                'score': d['score'],
            }
            for d in destinations[:10]
        ])
    
    @action(detail=False, methods=['get'])
    def best_accommodations(self, request):
        """Meilleurs hébergements recommandés"""
        engine = RecommendationEngine(request.user)
        
        accommodations = []
        for hebergement in Hebergement.objects.all():
            score = engine.calculate_hebergement_score(hebergement)
            if score > 40:
                accommodations.append({
                    'hebergement': hebergement,
                    'score': score,
                })
        
        accommodations.sort(key=lambda x: x['score'], reverse=True)
        
        return Response([
            {
                'id': h['hebergement'].id,
                'nom': h['hebergement'].nom_hebergement,
                'type': h['hebergement'].type_hebergement,
                'etoiles': h['hebergement'].etoiles,
                'prix_par_nuit': float(h['hebergement'].prix_par_nuit),
                'score': h['score'],
            }
            for h in accommodations[:10]
        ])
    
    @action(detail=False, methods=['post'])
    def mark_viewed(self, request):
        """Marquer une recommandation comme vue"""
        recommendation_id = request.data.get('recommendation_id')
        
        try:
            recommendation = Recommendation.objects.get(
                id=recommendation_id,
                user=request.user
            )
            recommendation.is_viewed = True
            recommendation.viewed_at = timezone.now()
            recommendation.save()
            
            return Response({'success': True})
        except Recommendation.DoesNotExist:
            return Response(
                {'error': 'Recommandation non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def submit_feedback(self, request):
        """Soumettre un feedback sur une recommandation"""
        recommendation_id = request.data.get('recommendation_id')
        feedback_type = request.data.get('feedback_type')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        
        try:
            recommendation = Recommendation.objects.get(
                id=recommendation_id,
                user=request.user
            )
            
            feedback, created = RecommendationFeedback.objects.update_or_create(
                recommendation=recommendation,
                defaults={
                    'feedback_type': feedback_type,
                    'rating': rating,
                    'comment': comment,
                }
            )
            
            return Response({
                'success': True,
                'message': 'Feedback enregistré'
            })
        except Recommendation.DoesNotExist:
            return Response(
                {'error': 'Recommandation non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )


@login_required
@require_http_methods(["GET"])
def api_recommendations_json(request):
    """API JSON pour les recommandations"""
    engine = RecommendationEngine(request.user)
    recommendations = engine.generate_recommendations(limit=10)
    
    return JsonResponse({
        'count': len(recommendations),
        'recommendations': [
            {
                'id': rec['item'].id,
                'titre': rec['item'].titre,
                'prix': float(rec['item'].prix_par_personne),
                'score': rec['score'],
                'reason': rec['reason'],
                'destinations': list(rec['item'].nom_destinations.values_list('nom_destination', flat=True)),
            }
            for rec in recommendations
        ]
    })
