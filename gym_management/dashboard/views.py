from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    role = request.user.role
    if role == 'admin':
        return render(request, 'admin_dashboard.html')
    elif role == 'trainer':
        return render(request, 'trainer_dashboard.html')
    elif role == 'member':
        return render(request, 'member_dashboard.html')
    return render(request, 'login.html')
