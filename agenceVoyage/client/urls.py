from django.urls import path
from . import views

app_name = 'client'

urlpatterns = [
    path('login/', views.loginUser, name='login'),
    path('signup/', views.addUser, name='signup'),
    path('logout/', views.logoutUser, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_update, name='profile_edit'),
    path('users/', views.listUsers, name='list_users'),
    path('users/<int:user_id>/', views.updateUser, name='update_user'),
    path('users/<int:user_id>/delete/', views.deleteUser, name='delete_user'),
]
