from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from users.forms import CustomUserCreationForm
from users.models import CustomUser

# Home page
def home(request):
    return render(request, 'home.html')

# Payment page (mock)
def payment(request):
    return render(request, 'payment.html')

# Registration page
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# Login page
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            pass
    return render(request, 'login.html')

# Logout
def user_logout(request):
    logout(request)
    return redirect('login')

# Role-based dashboard redirect
@login_required
def dashboard(request):
    role = request.user.role
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'trainer':
        return render(request, 'trainer_dashboard.html')
    elif role == 'member':
        return render(request, 'member_dashboard.html')
    else:
        return redirect('home')

# Admin dashboard: view users
@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('dashboard')

    # Only show trainers and members
    users = CustomUser.objects.filter(role__in=['trainer', 'member'])

    return render(request, 'admin_dashboard.html', {'users': users})

# Admin: add new user
@login_required
def add_user(request):
    if request.user.role != 'admin':
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User added successfully.")
            return redirect('admin_dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'admin_add_user.html', {'form': form})

# Admin: delete user
@login_required
def delete_user(request, user_id):
    if request.user.role != 'admin':
        return redirect('dashboard')

    user = get_object_or_404(CustomUser, id=user_id)

    if user.role != 'admin':
        user.delete()
        messages.success(request, "User deleted successfully.")

    return redirect('admin_dashboard')
