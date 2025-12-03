from django.contrib import admin
from .models import FidelityTierConfig, LoyaltyProgram, PointsTransaction


@admin.register(FidelityTierConfig)
class FidelityTierConfigAdmin(admin.ModelAdmin):
    list_display = ['tier', 'points_requis_min', 'points_requis_max', 'pourcentage_remise', 'bonus_multiplier']
    list_editable = ['pourcentage_remise', 'bonus_multiplier']
    ordering = ['points_requis_min']


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ['user', 'tier', 'points', 'totalEarnedPoints', 'totalRedeemedPoints', 'enrolled_at']
    list_filter = ['tier', 'enrolled_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['totalEarnedPoints', 'totalRedeemedPoints', 'enrolled_at', 'last_tier_update']


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    list_display = ['loyalty_program', 'transaction_type', 'points_amount', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['loyalty_program__user__username', 'description']
    readonly_fields = ['created_at']
