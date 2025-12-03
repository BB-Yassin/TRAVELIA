from rest_framework import serializers
from .models import LoyaltyProgram, PointsTransaction, FidelityTierConfig


class FidelityTierConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = FidelityTierConfig
        fields = ['tier', 'points_requis_min', 'points_requis_max', 'pourcentage_remise', 'bonus_multiplier']


class PointsTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointsTransaction
        fields = ['id', 'transaction_type', 'points_amount', 'description', 'created_at']


class LoyaltyProgramSerializer(serializers.ModelSerializer):
    tier_config = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = LoyaltyProgram
        fields = [
            'id', 'tier', 'points', 'totalEarnedPoints', 'totalRedeemedPoints',
            'enrolled_at', 'pointsExpiryDate', 'tier_config', 'discount_percentage'
        ]
    
    def get_tier_config(self, obj):
        tier_config = obj.get_tier_config()
        if tier_config:
            return FidelityTierConfigSerializer(tier_config).data
        return None
    
    def get_discount_percentage(self, obj):
        return float(obj.get_discount_percentage())
