from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import LoyaltyProgram, PointsTransaction, FidelityTierConfig
from .serializers import (
    LoyaltyProgramSerializer, 
    PointsTransactionSerializer,
    FidelityTierConfigSerializer
)


@login_required
@require_http_methods(["GET"])
def loyalty_dashboard(request):
    """Vue du tableau de bord de fidélité client"""
    try:
        loyalty = LoyaltyProgram.objects.get(user=request.user)
    except LoyaltyProgram.DoesNotExist:
        # Créer automatiquement le programme de fidélité
        loyalty = LoyaltyProgram.objects.create(user=request.user)
    
    tier_config = loyalty.get_tier_config()
    
    # Calculer la progression vers le prochain tier
    next_tier = FidelityTierConfig.objects.filter(
        points_requis_min__gt=loyalty.totalEarnedPoints
    ).order_by('points_requis_min').first()
    
    percentage = 0
    if next_tier:
        current_range = next_tier.points_requis_min - (
            FidelityTierConfig.objects.filter(
                points_requis_min__lt=loyalty.totalEarnedPoints
            ).order_by('-points_requis_min').first().points_requis_min
            if FidelityTierConfig.objects.filter(
                points_requis_min__lt=loyalty.totalEarnedPoints
            ).exists() else 0
        )
        current_progress = loyalty.totalEarnedPoints - (
            FidelityTierConfig.objects.filter(
                points_requis_min__lt=loyalty.totalEarnedPoints
            ).order_by('-points_requis_min').first().points_requis_min
            if FidelityTierConfig.objects.filter(
                points_requis_min__lt=loyalty.totalEarnedPoints
            ).exists() else 0
        )
        percentage = int((current_progress / current_range * 100)) if current_range > 0 else 0
    
    progression = {
        'current_points': loyalty.totalEarnedPoints,
        'next_tier': next_tier,
        'points_needed': next_tier.points_requis_min - loyalty.totalEarnedPoints if next_tier else 0,
        'percentage': min(percentage, 100),
        'next_tier_min': next_tier.points_requis_min if next_tier else loyalty.totalEarnedPoints,
    }
    
    transactions = loyalty.transactions.all()[:10]
    
    context = {
        'loyalty': loyalty,
        'tier_config': tier_config,
        'progression': progression,
        'available_points': loyalty.points,
        'redeemed_points': loyalty.totalRedeemedPoints,
        'transactions': transactions,
    }
    
    return render(request, 'programmeFidilite/dashboard.html', context)


@login_required
@require_http_methods(["GET"])
def loyalty_points_history(request):
    """Historique des transactions de points"""
    loyalty = get_object_or_404(LoyaltyProgram, user=request.user)
    transactions = loyalty.transactions.all()[:50]  # Dernières 50 transactions
    
    # Statistiques
    stats = {
        'total_earned': transactions.filter(transaction_type='earn').aggregate(Sum('points_amount'))['points_amount__sum'] or 0,
        'total_redeemed': transactions.filter(transaction_type='redeem').aggregate(Sum('points_amount'))['points_amount__sum'] or 0,
        'total_expired': transactions.filter(transaction_type='expire').aggregate(Sum('points_amount'))['points_amount__sum'] or 0,
    }
    
    context = {
        'loyalty': loyalty,
        'transactions': transactions,
        'stats': stats,
    }
    
    return render(request, 'programmeFidilite/points_history.html', context)


@login_required
@require_http_methods(["GET"])
def loyalty_tier_info(request):
    """Informations détaillées sur les tiers de fidélité"""
    loyalty = get_object_or_404(LoyaltyProgram, user=request.user)
    all_tiers = FidelityTierConfig.objects.all()
    current_tier = loyalty.get_tier_config()
    
    context = {
        'loyalty': loyalty,
        'current_tier': current_tier,
        'all_tiers': all_tiers,
        'current_points': loyalty.totalEarnedPoints,
    }
    
    return render(request, 'programmeFidilite/tier_info.html', context)


@login_required
@require_http_methods(["GET"])
def redeem_points_view(request):
    """Vue pour utiliser les points"""
    loyalty = get_object_or_404(LoyaltyProgram, user=request.user)
    
    context = {
        'loyalty': loyalty,
        'available_points': loyalty.points,
        'discount_percentage': loyalty.get_discount_percentage(),
        'tier_config': loyalty.get_tier_config(),
    }
    
    return render(request, 'programmeFidilite/redeem_points.html', context)


# ============== API VIEWS (REST Framework) ==============

class LoyaltyProgramViewSet(viewsets.ViewSet):
    """API pour gérer le programme de fidélité"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_loyalty(self, request):
        """Retourne les infos de fidélité de l'utilisateur"""
        try:
            loyalty = LoyaltyProgram.objects.get(user=request.user)
        except LoyaltyProgram.DoesNotExist:
            return Response(
                {'error': 'Programme de fidélité non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = LoyaltyProgramSerializer(loyalty)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def points_breakdown(self, request):
        """Détails des points (disponibles, utilisés, expirés)"""
        try:
            loyalty = LoyaltyProgram.objects.get(user=request.user)
        except LoyaltyProgram.DoesNotExist:
            return Response(
                {'error': 'Programme de fidélité non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = {
            'available_points': loyalty.points,
            'total_earned': loyalty.totalEarnedPoints,
            'total_redeemed': loyalty.totalRedeemedPoints,
            'tier': loyalty.tier,
            'tier_config': FidelityTierConfigSerializer(loyalty.get_tier_config()).data if loyalty.get_tier_config() else None,
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def tier_progression(self, request):
        """Progression vers le prochain tier"""
        try:
            loyalty = LoyaltyProgram.objects.get(user=request.user)
        except LoyaltyProgram.DoesNotExist:
            return Response(
                {'error': 'Programme de fidélité non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        next_tier = FidelityTierConfig.objects.filter(
            points_requis_min__gt=loyalty.totalEarnedPoints
        ).order_by('points_requis_min').first()
        
        data = {
            'current_tier': loyalty.tier,
            'current_points': loyalty.totalEarnedPoints,
            'next_tier': next_tier.tier if next_tier else None,
            'points_for_next_tier': next_tier.points_requis_min if next_tier else None,
            'points_needed': next_tier.points_requis_min - loyalty.totalEarnedPoints if next_tier else 0,
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def transactions(self, request):
        """Historique des transactions"""
        try:
            loyalty = LoyaltyProgram.objects.get(user=request.user)
        except LoyaltyProgram.DoesNotExist:
            return Response(
                {'error': 'Programme de fidélité non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        transactions = loyalty.transactions.all()[:50]
        serializer = PointsTransactionSerializer(transactions, many=True)
        
        return Response({
            'count': loyalty.transactions.count(),
            'transactions': serializer.data,
        })
    
    @action(detail=False, methods=['post'])
    def redeem(self, request):
        """Utiliser des points pour une réduction"""
        try:
            loyalty = LoyaltyProgram.objects.get(user=request.user)
        except LoyaltyProgram.DoesNotExist:
            return Response(
                {'error': 'Programme de fidélité non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        points_to_redeem = request.data.get('points', 0)
        
        if not isinstance(points_to_redeem, int) or points_to_redeem <= 0:
            return Response(
                {'error': 'Montant invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if points_to_redeem > loyalty.points:
            return Response(
                {'error': f'Points insuffisants. Vous avez {loyalty.points} points'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        discount_amount = loyalty.redeem_points(points_to_redeem)
        
        # Créer une transaction
        PointsTransaction.objects.create(
            loyalty_program=loyalty,
            transaction_type='redeem',
            points_amount=points_to_redeem,
            description=f'Rédemption de {points_to_redeem} points pour {discount_amount}€'
        )
        
        return Response({
            'success': True,
            'points_redeemed': points_to_redeem,
            'discount_amount': float(discount_amount),
            'remaining_points': loyalty.points,
        })
    
    @action(detail=False, methods=['get'])
    def all_tiers(self, request):
        """Liste de tous les tiers disponibles"""
        tiers = FidelityTierConfig.objects.all()
        serializer = FidelityTierConfigSerializer(tiers, many=True)
        
        return Response(serializer.data)


# ============== HELPER VIEWS ==============

@login_required
@require_http_methods(["GET"])
def api_loyalty_summary(request):
    """API endpoint JSON pour le résumé de fidélité"""
    try:
        loyalty = LoyaltyProgram.objects.get(user=request.user)
    except LoyaltyProgram.DoesNotExist:
        return JsonResponse({'error': 'Programme de fidélité non trouvé'}, status=404)
    
    next_tier = FidelityTierConfig.objects.filter(
        points_requis_min__gt=loyalty.totalEarnedPoints
    ).order_by('points_requis_min').first()
    
    return JsonResponse({
        'tier': loyalty.tier,
        'available_points': loyalty.points,
        'total_earned_points': loyalty.totalEarnedPoints,
        'total_redeemed_points': loyalty.totalRedeemedPoints,
        'discount_percentage': float(loyalty.get_discount_percentage()),
        'next_tier': next_tier.tier if next_tier else None,
        'points_needed_for_next_tier': next_tier.points_requis_min - loyalty.totalEarnedPoints if next_tier else 0,
    })
