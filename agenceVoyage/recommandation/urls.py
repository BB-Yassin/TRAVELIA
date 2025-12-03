from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'recommandation'

router = DefaultRouter()
router.register(r'api', views.RecommendationViewSet, basename='recommendation')

urlpatterns = [
    # Web views
    path('', views.get_recommendations, name='recommendations'),
    path('detail/<int:recommendation_id>/', views.recommendation_detail, name='detail'),
    
    # JSON API
    path('api/json/', views.api_recommendations_json, name='api_json'),
] + router.urls
