from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from .models import Preference
from .forms import PreferenceForm
from .decorators import login_required_modal
import logging

logger = logging.getLogger(__name__)

@login_required_modal
def preference_list(request):
    """List all preferences (admin view for all users)"""
    try:
        if not request.user.is_staff:
            return redirect('preferences:view')
        
        preferences = Preference.objects.all()
        logger.info(f"Admin {request.user.email} viewed preferences list")
        
        return render(request, 'preferences/preference_list.html', {
            'preferences': preferences
        })
    except Exception as e:
        logger.error(f"Error in preference_list: {str(e)}")
        messages.error(request, "An error occurred while loading preferences.")
        return redirect('home')

@login_required_modal
def preference_view(request):
    """View user's preferences"""
    try:
        preference = Preference.objects.get(user=request.user)
        logger.info(f"User {request.user.email} viewed their preferences")
        
        return render(request, 'preferences/preference_detail.html', {
            'preference': preference
        })
    except Preference.DoesNotExist:
        logger.warning(f"User {request.user.email} has no preferences set")
        messages.info(request, "You haven't set your preferences yet. Create them now!")
        return redirect('preferences:create')
    except Exception as e:
        logger.error(f"Error in preference_view: {str(e)}")
        messages.error(request, "An error occurred while viewing preferences.")
        return redirect('home')

@login_required_modal
def preference_create(request):
    """Create user preferences"""
    try:
        # Check if user already has preferences
        try:
            preference = Preference.objects.get(user=request.user)
            logger.warning(f"User {request.user.email} tried to create duplicate preferences")
            messages.warning(request, "You already have preferences. Use the edit option instead.")
            return redirect('preferences:edit')
        except Preference.DoesNotExist:
            pass
        
        if request.method == 'POST':
            form = PreferenceForm(request.POST)
            if form.is_valid():
                preference = form.save(commit=False)
                preference.user = request.user
                preference.save()
                
                logger.info(f"User {request.user.email} created preferences")
                messages.success(request, "✅ Preferences created successfully!")
                return redirect('preferences:view')
            else:
                logger.warning(f"Form validation failed for user {request.user.email}: {form.errors}")
        else:
            form = PreferenceForm()
        
        return render(request, 'preferences/preference_form.html', {
            'form': form,
            'title': 'Create Your Preferences',
            'action': 'Create'
        })
    except Exception as e:
        logger.error(f"Error in preference_create: {str(e)}")
        messages.error(request, "An error occurred while creating preferences.")
        return redirect('home')

@login_required_modal
def preference_edit(request):
    """Edit user preferences"""
    try:
        preference = get_object_or_404(Preference, user=request.user)
        
        if request.method == 'POST':
            form = PreferenceForm(request.POST, instance=preference)
            if form.is_valid():
                form.save()
                
                logger.info(f"User {request.user.email} updated preferences")
                messages.success(request, "✅ Preferences updated successfully!")
                return redirect('preferences:view')
            else:
                logger.warning(f"Form validation failed for user {request.user.email}: {form.errors}")
        else:
            form = PreferenceForm(instance=preference)
        
        return render(request, 'preferences/preference_form.html', {
            'form': form,
            'preference': preference,
            'title': 'Edit Your Preferences',
            'action': 'Update'
        })
    except Preference.DoesNotExist:
        logger.warning(f"User {request.user.email} tried to edit non-existent preferences")
        messages.warning(request, "You don't have preferences yet. Create them first!")
        return redirect('preferences:create')
    except Exception as e:
        logger.error(f"Error in preference_edit: {str(e)}")
        messages.error(request, "An error occurred while editing preferences.")
        return redirect('home')


def preferences_edit(request):
    """Edit user preferences - new template version"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        preference, created = Preference.objects.get_or_create(user=request.user)
    except:
        preference = None
    
    if request.method == 'POST':
        preference.travel_class = request.POST.get('travel_class', preference.travel_class if preference else 'ECONOMY')
        preference.meal_preference = request.POST.get('meal_preference', preference.meal_preference if preference else 'NON_VEGETARIAN')
        preference.seat_preference = request.POST.get('seat_preference', preference.seat_preference if preference else 'AISLE')
        preference.price_range = request.POST.get('price_range', preference.price_range if preference else 'STANDARD')
        preference.user = request.user
        preference.save()
        
        messages.success(request, "Preferences updated successfully!")
        return redirect('profile')
    
    from recommandation.views import RecommendationEngine
    engine = RecommendationEngine(request.user)
    recommendations = engine.generate_recommendations(limit=5)
    
    context = {
        'preference': preference,
        'recommendations': recommendations,
    }
    
    return render(request, 'preferences/edit.html', context)

@login_required_modal
def preference_delete(request):
    """Delete user preferences"""
    try:
        preference = get_object_or_404(Preference, user=request.user)
        
        if request.method == 'POST':
            user_email = preference.user.email
            preference.delete()
            
            logger.info(f"User {user_email} deleted their preferences")
            messages.success(request, "✅ Preferences deleted successfully!")
            return redirect('home')
        
        return render(request, 'preferences/preference_confirm_delete.html', {
            'preference': preference
        })
    except Preference.DoesNotExist:
        logger.warning(f"User {request.user.email} tried to delete non-existent preferences")
        messages.warning(request, "Preferences not found!")
        return redirect('home')
    except Exception as e:
        logger.error(f"Error in preference_delete: {str(e)}")
        messages.error(request, "An error occurred while deleting preferences.")
        return redirect('home')
