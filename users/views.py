from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import CustomUserCreationForm, UserUpdateForm
from .models import RegistrationCode

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Get the registration code
            code = form.cleaned_data['registration_code']

            # Create the user
            user = form.save(commit=False)
            user.is_student = True
            user.terms_accepted = True  # Set terms as accepted
            user.save()

            # Generate student ID
            user.student_id = f"AFIMPP{user.id:05d}"
            user.save()

            # Mark the registration code as used
            try:
                reg_code = RegistrationCode.objects.get(code=code)
                reg_code.is_used = True
                reg_code.used_by = user
                reg_code.used_at = timezone.now()
                reg_code.save()
            except RegistrationCode.DoesNotExist:
                pass  # Already validated in form

            # Automatically log the user in
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
            return redirect('dashboard')  # Redirect to dashboard instead of home
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
    }
    return render(request, 'users/register.html', context)


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'users/login.html')


@login_required
def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'users/profile.html', context)