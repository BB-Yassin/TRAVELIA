from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import User
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from django.urls import reverse
import logging
from django.contrib.auth import logout

logger = logging.getLogger(__name__)

def loginUser(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        logger.info(f"Login attempt: email={email}")

        if not all([email, password]):
            logger.warning(f"Missing fields: email={bool(email)}, password={bool(password)}")
            messages.error(request, "Email and password are required.")
            return HttpResponseRedirect(reverse('home') + '#login')

        try:
            # Authenticate using email
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                logger.info(f"User logged in: id={user.id}, email={user.email}")
                messages.success(request, f"Welcome back, {user.fullname}!")
                return redirect("home")
            else:
                logger.warning(f"Authentication failed for email: {email}")
                messages.error(request, "Invalid email or password.")
                return HttpResponseRedirect(reverse('home') + '#login')
        except Exception as e:
            logger.error(f"Login error: {type(e).__name__}: {str(e)}", exc_info=True)
            messages.error(request, "Error during login. Please try again.")
            return HttpResponseRedirect(reverse('home') + '#login')

    return render(request, "login_signup.html")


def logoutUser(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out.')
    return redirect('home')

def addUser(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        logger.info(f"Signup attempt: email={email}, first_name={first_name}, last_name={last_name}")

        if not all([first_name, last_name, email, password, password_confirm]):
            logger.warning(f"Missing fields: first_name={bool(first_name)}, last_name={bool(last_name)}, email={bool(email)}, password={bool(password)}")
            messages.error(request, "All fields are required.")
            return HttpResponseRedirect(reverse('home') + '#signup')

        if password != password_confirm:
            logger.warning(f"Password mismatch for email: {email}")
            messages.error(request, "Passwords do not match.")
            return HttpResponseRedirect(reverse('home') + '#signup')

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return HttpResponseRedirect(reverse('home') + '#signup')

        if User.objects.filter(email=email).exists():
            logger.warning(f"Email already exists: {email}")
            messages.error(request, "A user with this email already exists.")
            return HttpResponseRedirect(reverse('home') + '#signup')

        try:
            logger.info(f"Creating user with email: {email}")
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role="CLIENT"
            )
            logger.info(f"User created successfully: id={user.id}, email={user.email}, fullname={user.fullname}")
            messages.success(request, f"Welcome, {user.fullname}! Account created successfully. Please log in.")
            # Redirect to home with login modal hash
            return HttpResponseRedirect(reverse('home') + '#login')
        except Exception as e:
            logger.error(f"User creation error: {type(e).__name__}: {str(e)}", exc_info=True)
            messages.error(request, "Error creating account. Please try again.")
            return HttpResponseRedirect(reverse('home') + '#signup')

    return render(request, "login_signup.html")

def updateUser(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.first_name = request.POST.get('name')
        user.last_name = request.POST.get('lastname')
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        user.address = request.POST.get('address')
        user.phone_number = request.POST.get('phone_number')

        user.fullname = f"{user.first_name} {user.last_name}"

        if User.objects.exclude(id=user_id).filter(email=user.email).exists():
            messages.error(request, "This email is already used by another user.")
            return render(request, "update_user.html", {"user": user})

        user.save()
        messages.success(request, "User updated successfully!")
        return redirect("list_users")

    return render(request, "update_user.html", {"user": user})

def listUsers(request):
    users = User.objects.all().order_by('-created_at')
    return render(request, "list_users.html", {"users": users})


def profile(request):
    # View current user's profile
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view your profile.")
        return redirect('home')
    
    user = request.user
    loyalty = getattr(user, 'loyalty_program', None)
    preference = getattr(user, 'preference', None)
    transactions = None
    bookings = None
    
    if loyalty:
        transactions = loyalty.transactions.all()[:10]
    
    if hasattr(user, 'reservations'):
        bookings = user.reservations.all()[:5]
    
    context = {
        'user': user,
        'loyalty': loyalty,
        'preference': preference,
        'transactions': transactions,
        'bookings': bookings,
    }
    
    return render(request, 'client/profile.html', context)


def profile_update(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to edit your profile.")
        return redirect('home')

    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('name', user.first_name)
        user.last_name = request.POST.get('lastname', user.last_name)
        new_email = request.POST.get('email', user.email)
        # Check uniqueness
        if User.objects.exclude(id=user.id).filter(email=new_email).exists():
            messages.error(request, "This email is already used by another user.")
            return render(request, 'profile_edit.html', {'user_obj': user})
        user.email = new_email
        user.address = request.POST.get('address', user.address)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        pwd = request.POST.get('password', '')
        if pwd:
            user.set_password(pwd)
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    return render(request, 'profile_edit.html', {'user_obj': user})

def deleteUser(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect("list_users")
