from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import timedelta
from django.utils import timezone


class loyaltyTier(models.TextChoices):  
    BRONZE = 'BRONZE', 'Bronze'
    SILVER = 'SILVER', 'Silver'
    GOLD = 'GOLD', 'Gold'
    PLATINUM = 'PLATINUM', 'Platinum'   


class FidelityTierConfig(models.Model):
    """Configuration des tiers de fidélité avec points et avantages"""
    TIER_CHOICES = [
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
    ]
    
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    points_requis_min = models.PositiveIntegerField()
    points_requis_max = models.PositiveIntegerField()
    pourcentage_remise = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    bonus_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.0, help_text="Multiplicateur de points")
    
    def __str__(self):
        return f"{self.tier} ({self.points_requis_min}-{self.points_requis_max} pts) - {self.pourcentage_remise}% remise"
    
    class Meta:
        ordering = ['points_requis_min']


class LoyaltyProgram(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loyalty_program')
    points = models.PositiveIntegerField(default=0)
    enrolled_at = models.DateTimeField(auto_now_add=True) 
    tier = models.CharField(
        max_length=10,
        choices=loyaltyTier.choices,
        default=loyaltyTier.BRONZE,
    )
    totalEarnedPoints = models.PositiveIntegerField(default=0)
    totalRedeemedPoints = models.PositiveIntegerField(default=0)
    pointsExpiryDate = models.DateTimeField(null=True, blank=True)
    last_tier_update = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"LoyaltyProgram for {self.user.get_full_name()} - Tier: {self.tier}"
    
    def get_tier_config(self):
        """Récupère la configuration du tier actuel"""
        return FidelityTierConfig.objects.filter(tier=self.tier).first()
    
    def update_tier(self):
        """Met à jour le tier en fonction des points totaux"""
        tier_config = FidelityTierConfig.objects.filter(
            points_requis_min__lte=self.totalEarnedPoints
        ).order_by('-points_requis_min').first()
        
        if tier_config:
            self.tier = tier_config.tier
            self.last_tier_update = timezone.now()
            self.save()
    
    def add_points(self, reservation):
        """
        Ajoute les points à partir d'une réservation
        Points = prix * 10 + bonus 5 étoiles (50% bonus)
        """
        points_base = int(reservation.prix_total * 10)
        
        # Bonus 50% si hébergement 5 étoiles
        bonus = int(points_base * 0.5) if reservation.hebergement.etoiles == 5 else 0
        
        total_points = points_base + bonus
        
        # Appliquer le multiplicateur du tier
        tier_config = self.get_tier_config()
        if tier_config:
            total_points = int(total_points * tier_config.bonus_multiplier)
        
        self.points += total_points
        self.totalEarnedPoints += total_points
        self.pointsExpiryDate = timezone.now() + timedelta(days=365)
        
        self.update_tier()
        self.save()
        
        return total_points
    
    def redeem_points(self, points_to_redeem):
        """
        Convertit les points en réduction
        1 point = 0.01€ de réduction
        """
        if points_to_redeem > self.points:
            return None
        
        reduction_amount = points_to_redeem * 0.01
        self.points -= points_to_redeem
        self.totalRedeemedPoints += points_to_redeem
        self.save()
        
        return reduction_amount
    
    def get_discount_percentage(self):
        """Retourne le pourcentage de remise selon le tier"""
        tier_config = self.get_tier_config()
        return tier_config.pourcentage_remise if tier_config else 0


class PointsTransaction(models.Model):
    """Historique des transactions de points"""
    TRANSACTION_TYPES = [
        ('earn', 'Points gagnés'),
        ('redeem', 'Points utilisés'),
        ('expire', 'Points expirés'),
        ('bonus', 'Bonus points'),
    ]
    
    loyalty_program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points_amount = models.PositiveIntegerField()
    reservation = models.ForeignKey('reservation.Reservation', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.loyalty_program.user.username} - {self.transaction_type}: {self.points_amount} pts"
    
    class Meta:
        ordering = ['-created_at']