import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from users.forms import CustomUserCreationForm
from users.models import CustomUser
from django.views.decorators.csrf import csrf_protect
from .models import Plan
from .forms import PlanUploadForm
from .models import Feedback
from users.models import Progress


def home(request):
    return render(request, 'home.html')

def payment(request):
    return render(request, 'payment.html')

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

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

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

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    
    users = CustomUser.objects.all()
    trainers = CustomUser.objects.filter(role='trainer')  # ✅ Add this line
    return render(request, 'admin_dashboard.html', {'users': users, 'trainers': trainers})


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

@login_required
def delete_user(request, user_id):
    if request.user.role != 'admin':
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, id=user_id)
    if user.role != 'admin':
        user.delete()
        messages.success(request, "User deleted successfully.")
    return redirect('admin_dashboard')

@login_required
def view_assigned_members(request):
    if request.user.role != 'trainer':
        return redirect('dashboard')
    
    members = CustomUser.objects.filter(role='member', trainer=request.user)
    return render(request, 'trainer_assigned_members.html', {'members': members})

@login_required
@csrf_protect
def assign_trainer(request, user_id):
    if request.user.role != 'admin':
        return redirect('dashboard')

    member = get_object_or_404(CustomUser, id=user_id, role='member')

    if request.method == 'POST':
        trainer_id = request.POST.get('trainer_id')
        if trainer_id:
            trainer = CustomUser.objects.filter(id=trainer_id, role='trainer').first()
            if trainer:
                member.trainer = trainer
                member.save()
                messages.success(request, f"{member.username} assigned to {trainer.username}.")
        else:
            member.trainer = None
            member.save()
            messages.success(request, f"{member.username} unassigned from any trainer.")
    
    return redirect('admin_dashboard')


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def generate_mock_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gym_mock_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Report: Gym Users'])

    # Trainers Section
    writer.writerow([])
    writer.writerow(['--- Trainers ---'])
    writer.writerow(['Username', 'Name', 'Experience', 'Phone', 'Email'])
    trainers = CustomUser.objects.filter(role='trainer')
    for t in trainers:
        writer.writerow([t.username, t.name, t.experience, t.phone, t.email])

    # Members Section
    writer.writerow([])
    writer.writerow(['--- Members ---'])
    writer.writerow(['Username', 'Name', 'Age', 'Weight', 'Height', 'Trainer'])
    members = CustomUser.objects.filter(role='member')
    for m in members:
        writer.writerow([
            m.username, m.name, m.age, m.weight, m.height,
            m.trainer.name if m.trainer else 'Not Assigned'
        ])

    return response


def is_admin_or_trainer(user):
    return user.is_authenticated and (user.role == 'admin' or user.role == 'trainer')


@login_required
def upload_plan(request):
    if request.user.role != 'trainer':
        return redirect('dashboard:trainer_dashboard')

    assigned_members = CustomUser.objects.filter(trainer=request.user, role='member')

    if request.method == 'POST':
        form = PlanUploadForm(request.POST, request.FILES)
        form.fields['member'].queryset = assigned_members  # limit dropdown

        if form.is_valid():
            selected_member = form.cleaned_data['member']
            if selected_member.trainer != request.user:
                messages.error(request, "You can only upload plans for your assigned members.")
                return redirect('upload_plan')
            plan = form.save(commit=False)
            plan.trainer = request.user
            plan.save()
            messages.success(request, "Plan uploaded successfully.")
            return redirect('upload_plan')
    else:
        form = PlanUploadForm()
        form.fields['member'].queryset = assigned_members  # limit dropdown

    return render(request, 'upload_plan.html', {'form': form})

@login_required
def view_my_plans(request):         
    if request.user.role != 'member':
        return redirect('dashboard')
    plans = Plan.objects.filter(member=request.user)
    return render(request, 'view_my_plans.html', {'plans': plans})

@login_required
def submit_feedback(request):
    if request.user.role != 'member':
        return redirect('dashboard')  # Prevent non-members

    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            Feedback.objects.create(member=request.user, message=message)
            messages.success(request, "Feedback submitted successfully!")
            return redirect('submit_feedback')
        else:
            messages.error(request, "Please enter your feedback.")
    return render(request, 'member_feedback.html')


@login_required
def view_feedbacks(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    feedbacks = Feedback.objects.select_related('member').all().order_by('-submitted_at')
    return render(request, 'admin_view_feedbacks.html', {'feedbacks': feedbacks})

@login_required
def member_progress(request):
    if request.user.role != 'member':
        return redirect('home')

    progresses = Progress.objects.filter(member=request.user).order_by('-date')

    if request.method == 'POST':
        try:
            weight = float(request.POST.get('weight'))
            height = float(request.POST.get('height'))
            notes = request.POST.get('notes', '')

            Progress.objects.create(member=request.user, weight=weight, height=height, notes=notes)
            messages.success(request, "Progress entry added successfully.")
            return redirect('member_progress')
        except ValueError:
            messages.error(request, "Please enter valid numeric values for weight and height.")

    return render(request, 'member_progress.html', {'progresses': progresses})

