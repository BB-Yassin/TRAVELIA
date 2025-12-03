from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse


def login_required_modal(view_func):
    """
    Decorator that checks if user is authenticated.
    If not, redirects to home with #login hash to trigger modal.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('home') + '#login')
        return view_func(request, *args, **kwargs)
    return wrapper
