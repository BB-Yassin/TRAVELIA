from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'programmeFidilite'

router = DefaultRouter()
router.register(r'api/loyalty', views.LoyaltyProgramViewSet, basename='loyalty')

urlpatterns = [
    # Web views
    path('dashboard/', views.loyalty_dashboard, name='loyalty_dashboard'),
    path('history/', views.loyalty_points_history, name='points_history'),
    path('tiers/', views.loyalty_tier_info, name='tier_info'),
    path('redeem/', views.redeem_points_view, name='redeem_points'),
    
    # JSON API endpoints
    path('api/summary/', views.api_loyalty_summary, name='api_summary'),
] + router.urls
