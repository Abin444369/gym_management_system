import csv
from django.urls import reverse
import razorpay
import json
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
from .models import MemberProgress
from django.conf import settings
from .models import Payment 
from .forms import PaymentPlanForm

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
client.set_app_details(app_details={"title": "Gym_Management_System", "version": "1.0"})


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

    progresses = MemberProgress.objects.filter(member=request.user).order_by('-date')

    if request.method == 'POST':
        try:
            progress = MemberProgress(
                member=request.user,
                weight=float(request.POST.get('weight')),
                height=float(request.POST.get('height')),
                notes=request.POST.get('notes', '')
            )
            progress.save()
            messages.success(request, "Progress entry added successfully.")
            return redirect('member_progress')
        except ValueError:
            messages.error(request, "Please enter valid numeric values for weight and height.")

    return render(request, 'member_progress.html', {'progresses': progresses})

@login_required
def add_progress(request, member_id):
    if request.user.role != 'trainer':
        messages.error(request, "Only trainers can add progress records.")
        return redirect('dashboard')

    member = get_object_or_404(CustomUser, id=member_id, role='member', trainer=request.user)

    if request.method == 'POST':
        try:
            progress = MemberProgress(
                member=member,
                trainer=request.user,
                weight=float(request.POST.get('weight')),
                height=float(request.POST.get('height')),
                performance=request.POST.get('performance'),
                attendance=request.POST.get('attendance') == 'on',
                notes=request.POST.get('notes', '')
            )
            progress.save()
            messages.success(request, f"Progress recorded for {member.username}")
            return redirect('view_progress', member_id=member_id)
        except ValueError:
            messages.error(request, "Please enter valid values.")
    
    return render(request, 'add_progress.html', {'member': member})
@login_required
def view_progress(request, member_id):
    member = get_object_or_404(CustomUser, id=member_id)
    
    if request.user.role == 'trainer' and member.trainer != request.user:
        messages.error(request, "You can only view progress for your assigned members.")
        return redirect('dashboard')
    
    if request.user.role == 'member' and request.user.id != member_id:
        messages.error(request, "You can only view your own progress.")
        return redirect('dashboard')
    
    progress_records = MemberProgress.objects.filter(member=member).order_by('-date')
    return render(request, 'view_progress.html', {
        'member': member,
        'progress_records': progress_records
    })
@login_required
def progress_list(request):
    if request.user.role == 'trainer':
        members = CustomUser.objects.filter(trainer=request.user, role='member')
    elif request.user.role == 'member':
        members = [request.user]
    else:
        members = CustomUser.objects.filter(role='member')
    
    return render(request, 'progress_list.html', {'members': members})

@login_required
def initiate_payment(request):
    if request.method == 'POST':
        form = PaymentPlanForm(request.POST)
        if form.is_valid():
            original_amount_in_rupees = form.get_amount() # Get amount in Rupees
            amount_in_paisa = int(original_amount_in_rupees * 100) # Convert to paisa for Razorpay # Razorpay expects amount in paisa
            currency = 'INR'
            
            # Create Razorpay Order
            order_data = {
                'amount': amount_in_paisa,
                'currency': currency,
                'receipt': f'receipt_for_{request.user.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'payment_capture': '1' # Auto capture payment
            }
            try:
                razorpay_order = client.order.create(order_data)

                # Save payment details in your database
                payment = Payment.objects.create(
                    user=request.user,
                    razorpay_order_id=razorpay_order['id'],
                    amount=form.get_amount(),
                    currency=currency
                )

                context = {
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'razorpay_order_id': razorpay_order['id'],
                    'amount': amount_in_paisa,
                    'display_amount': original_amount_in_rupees,
                    'currency': currency,
                    'name': request.user.name or request.user.username,
                    'email': request.user.email,
                    'phone': request.user.phone or '9999999999', # Provide a default if not available
                    'callback_url': request.build_absolute_uri(reverse('payment_success')),
                }
                return render(request, 'payment.html', context)
            except Exception as e:
                messages.error(request, f"Error initiating payment: {e}")
                return redirect('dashboard') # Or a dedicated error page
    else:
        form = PaymentPlanForm()
    return render(request, 'payment.html', {'form': form, 'razorpay_key_id': settings.RAZORPAY_KEY_ID})


@login_required
def payment_success(request):
    if request.method == 'POST':
        # This view is called by Razorpay's checkout.js on successful payment
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Verify the payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)

            # Update your payment record
            payment = get_object_or_404(Payment, razorpay_order_id=razorpay_order_id)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.paid = True
            payment.save()

            messages.success(request, "Payment successful! Thank you.")
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f"Payment verification failed: {e}")
            return redirect('dashboard')
    else:
        messages.error(request, "Invalid payment request.")
        return redirect('dashboard')

# --- Razorpay Webhook (Optional but Recommended for Production) ---
# This is a separate endpoint that Razorpay will call directly when payment status changes.
# It's more reliable than relying solely on client-side callbacks.

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from datetime import datetime
import hmac
import hashlib

@csrf_exempt
def razorpay_webhook(request):
    if request.method == 'POST':
        payload = request.body.decode('utf-8')
        # Get the Razorpay signature from the request header
        razorpay_signature = request.headers.get('x-razorpay-signature')

        # Construct the webhook signature
        expected_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if expected_signature == razorpay_signature:
            event = json.loads(payload)
            event_type = event['event']

            if event_type == 'payment.captured':
                payment_id = event['payload']['payment']['entity']['id']
                order_id = event['payload']['payment']['entity']['order_id']

                try:
                    payment_record = Payment.objects.get(razorpay_order_id=order_id)
                    payment_record.razorpay_payment_id = payment_id
                    payment_record.paid = True
                    payment_record.save()
                    # Log or perform further actions for successful payment
                    print(f"Webhook: Payment {payment_id} for order {order_id} captured successfully.")
                except Payment.DoesNotExist:
                    print(f"Webhook: Payment record for order {order_id} not found in DB.")
                except Exception as e:
                    print(f"Webhook: Error updating payment record: {e}")
            elif event_type == 'order.paid':
                order_id = event['payload']['order']['entity']['id']
                # Optionally handle order.paid event, similar to payment.captured
                print(f"Webhook: Order {order_id} marked as paid.")
            # Handle other events like payment.failed, refund.processed etc.
            # You might want to log these events for auditing.
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400, content="Invalid signature")
    return HttpResponse(status=405) # Method Not Allowed for GET requests