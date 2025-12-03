from django.urls import path
from . import views

app_name = 'preferences'

urlpatterns = [
    path('', views.preference_view, name='view'),
    path('list/', views.preference_list, name='list'),
    path('create/', views.preference_create, name='create'),
    path('edit/', views.preference_edit, name='edit'),
    path('edit-new/', views.preferences_edit, name='edit_new'),
    path('delete/', views.preference_delete, name='delete'),
    path('save/', views.preferences_edit, name='save'),
]
