from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Vehicle, Tracking, Order
from .forms import OrderForm, SupportForm, TrackingLookupForm, InvestmentForm, PaymentProofForm
from django.http import JsonResponse
import os
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.utils.dateformat import format as date_format
from .models import SupportMessage

User = get_user_model()


def homepage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    vehicles = Vehicle.objects.all()[:3]
    return render(request, 'home.html', {'vehicles': vehicles})


def vehicles_list(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'vehicles.html', {'vehicles': vehicles})


def buy_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    from_email = settings.DEFAULT_FROM_EMAIL
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            # send email to admin with order and address details
            subject = f'New vehicle order #{order.id}'
            body = f"""Order details:
Vehicle: {order.vehicle}
Name: {order.name}
Email: {order.email}
Phone: {order.phone}
Address: {order.address or 'Not provided'}

Please set crypto payment details in admin to proceed."""
            if settings.ADMIN_EMAIL:
                send_mail(subject, body, from_email, [settings.ADMIN_EMAIL])
            # send confirmation to user (only if email provided)
            if order.email:
                subject = 'Order Confirmation - Tesla Investment Platform'
                html_message = f"""
                <html>
                <body style="font-family: Arial, sans-serif; background-color: #000; color: #fff; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #1a1a1a; border: 1px solid #333; padding: 30px; border-radius: 8px;">
                        <h2 style="color: #fff; margin-bottom: 20px;">Order Confirmation</h2>
                        <p style="color: #ccc; line-height: 1.6;">Hi {order.name},</p>
                        <p style="color: #ccc; line-height: 1.6;">
                            Thank you for your order! We have received your request and are processing it.
                        </p>
                        <div style="background-color: #222; padding: 20px; border-radius: 6px; margin: 20px 0;">
                            <p style="color: #999; margin: 5px 0;">Order ID: <strong style="color: #fff;">#{order.id}</strong></p>
                            <p style="color: #999; margin: 5px 0;">Vehicle: <strong style="color: #fff;">{order.vehicle.name}</strong></p>
                            <p style="color: #999; margin: 5px 0;">Status: <strong style="color: #4ade80;">Received</strong></p>
                        </div>
                        <p style="color: #4ade80; line-height: 1.6;">✓ Payment details will be sent to you shortly.</p>
                        <p style="color: #ccc; font-size: 14px; margin-top: 20px;">If you have any questions, please contact our support team.</p>
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #333;">
                            <p style="color: #666; font-size: 12px; margin: 0;">Best regards,</p>
                            <p style="color: #666; font-size: 12px; margin: 0;">Tesla Investment Platform Team</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                from django.utils.html import strip_tags
                plain_message = strip_tags(html_message)
                send_mail(
                    subject,
                    plain_message,
                    from_email,
                    [order.email],
                    html_message=html_message,
                    fail_silently=True
                )
            return render(request, 'order_success.html', {'order': order})
    else:
        form = OrderForm(initial={'vehicle': vehicle})
    return render(request, 'buy.html', {'vehicle': vehicle, 'form': form})


def support_page(request):
    # Allow users to look up their past support messages by email or by client_id cookie
    lookup_email = request.GET.get('email')
    client_id = request.COOKIES.get('support_client_id')
    from_email = settings.DEFAULT_FROM_EMAIL
    messages = None
    if request.method == 'POST':
        form = SupportForm(request.POST)
        if form.is_valid():
            msg = form.save()
            if settings.ADMIN_EMAIL:
                send_mail(f'New support request #{msg.id}', msg.message, from_email, [settings.ADMIN_EMAIL])
            # send confirmation to user only if email present
            if msg.email:
                send_mail('Support request received', f'Thank you {msg.name}, we received your message.', from_email, [msg.email])
            # Show a clear success page with details and a link to view support history
            return render(request, 'support_success.html', {'message': msg, 'admin_email': settings.ADMIN_EMAIL})
    else:
        form = SupportForm()

    if client_id:
        messages = SupportMessage.objects.filter(client_id=client_id).order_by('-created_at')
    elif lookup_email:
        messages = SupportMessage.objects.filter(email__iexact=lookup_email).order_by('-created_at')

    return render(request, 'support.html', {'form': form, 'messages': messages, 'lookup_email': lookup_email})


def support_messages_api(request):
    """Return JSON list of support messages for a given email (for polling)."""
    # support lookup by client_id (preferred) or fallback to email
    client_id = request.GET.get('client_id')
    email = request.GET.get('email')
    if client_id:
        qs = SupportMessage.objects.filter(client_id=client_id).order_by('created_at')
    elif email:
        qs = SupportMessage.objects.filter(email__iexact=email).order_by('created_at')
    else:
        return JsonResponse({'error': 'client_id or email required'}, status=400)
    data = []
    for m in qs:
        data.append({
            'id': m.id,
            'name': m.name,
            'message': m.message,
            'created_at': date_format(m.created_at, 'Y-m-d H:i:s'),
            'admin_reply': m.admin_reply or '',
            'replied_at': date_format(m.replied_at, 'Y-m-d H:i:s') if m.replied_at else None,
        })
    return JsonResponse({'messages': data})


@require_POST
def support_send_api(request):
    """Accept POSTed support message (AJAX) and return the saved message as JSON."""
    # Accept optional client_id (for anonymous/browser-identified chats)
    client_id = request.POST.get('client_id')
    from_email = settings.DEFAULT_FROM_EMAIL
    # If client_id provided, we don't require email; but the form still includes email/name
    form = SupportForm(request.POST)
    if form.is_valid():
        msg = form.save(commit=False)
        if client_id:
            msg.client_id = client_id
            # ensure email field exists; if not present set to empty string
            if not msg.email:
                msg.email = ''
        msg.save()
        # send admin notification
        if settings.ADMIN_EMAIL:
            send_mail(f'New support request #{msg.id}', msg.message, from_email, [settings.ADMIN_EMAIL])
        # user confirmation only if email present
        if msg.email:
            send_mail('Support request received', f'Thank you {msg.name}, we received your message.', from_email, [msg.email])
        return JsonResponse({'ok': True, 'message': {
            'id': msg.id,
            'name': msg.name,
            'message': msg.message,
            'created_at': date_format(msg.created_at, 'Y-m-d H:i:s'),
            'admin_reply': '',
            'replied_at': None,
        }})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


def track_page(request):
    result = None
    not_found = False
    if request.method == 'POST':
        form = TrackingLookupForm(request.POST)
        if form.is_valid():
            tid = form.cleaned_data['tracking_id']
            try:
                result = Tracking.objects.get(tracking_id=tid)
            except Tracking.DoesNotExist:
                not_found = True
    else:
        form = TrackingLookupForm()
    stages = ['Order confirmed', 'Vehicle preparation', 'In transit', 'Out for delivery', 'Delivered']
    return render(request, 'track.html', {'form': form, 'result': result, 'not_found': not_found, 'stages': stages})


def invest_page(request):
    from_email = settings.DEFAULT_FROM_EMAIL
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"{reverse('main:login')}?next={reverse('main:invest')}")
        form = InvestmentForm(request.POST)
        if form.is_valid():
            inv = form.save()
            subj = f'New investment #{inv.id} - {inv.full_name}'
            body = f"Tier: {inv.tier}\nCapital: {inv.capital}\nName: {inv.full_name}\nEmail: {inv.email}\nPhone: {inv.phone}\nMessage: {inv.message}"
            if settings.ADMIN_EMAIL:
                send_mail(subj, body, from_email, [settings.ADMIN_EMAIL])
            # send confirmation to user (only if email provided)
            if inv.email:
                send_mail('Investment received', f'Thank you {inv.full_name}, we received your investment submission.', from_email, [inv.email])
            return render(request, 'invest_success.html', {'investment': inv})
    else:
        form = InvestmentForm()
    tiers = {
        'bronze': {'min': 2000, 'suggested': '2,000-4,999', 'benefits': 'Monthly updates'},
        'silver': {'min': 5000, 'suggested': '5,000-19,999', 'benefits': 'Quarterly insights'},
        'gold': {'min': 20000, 'suggested': '20,000+', 'benefits': 'Priority briefings'},
    }
    return render(request, 'invest.html', {'form': form, 'tiers': tiers})


def email_debug(request):
    """Return current email-related settings and DJANGO_* env vars."""
    data = {
        'settings': {
            'EMAIL_BACKEND': settings.EMAIL_BACKEND,
            'EMAIL_HOST': settings.EMAIL_HOST,
            'EMAIL_PORT': settings.EMAIL_PORT,
            'EMAIL_HOST_USER': settings.EMAIL_HOST_USER,
            'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
            'ADMIN_EMAIL': settings.ADMIN_EMAIL,
            'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', None),
            'EMAIL_USE_SSL': getattr(settings, 'EMAIL_USE_SSL', None),
        },
        'env': {k: os.environ.get(k) for k in [
            'DJANGO_EMAIL_BACKEND',
            'DJANGO_EMAIL_HOST',
            'DJANGO_EMAIL_PORT',
            'DJANGO_EMAIL_USER',
            'DJANGO_EMAIL_PASSWORD',
            'DJANGO_DEFAULT_FROM',
            'DJANGO_ADMIN_EMAIL',
        ]},
    }
    return JsonResponse(data)


def email_test(request):
    """Send a test email using current SMTP settings and report status."""
    from_email = settings.DEFAULT_FROM_EMAIL
    admin_email = settings.ADMIN_EMAIL
    backend = settings.EMAIL_BACKEND
    host = settings.EMAIL_HOST
    user = settings.EMAIL_HOST_USER
    port = settings.EMAIL_PORT

    if not admin_email:
        return HttpResponse(f"Email test failed: ADMIN_EMAIL is empty. from='{from_email}' backend='{backend}' host='{host}' user='{user}' port='{port}'", status=500)
    try:
        sent = send_mail(
            'SMTP Test',
            f'This is a test email from Django. Sender={from_email}',
            from_email,
            [admin_email]
        )
        if sent:
            return HttpResponse(f"Email test sent successfully to {admin_email}. from='{from_email}' backend='{backend}' host='{host}' user='{user}' port='{port}'")
        return HttpResponse(f"Email test not sent (send_mail returned 0). from='{from_email}' backend='{backend}' host='{host}' user='{user}' port='{port}'", status=500)
    except Exception as e:
        return HttpResponse(f"Email test error: {e}. from='{from_email}' backend='{backend}' host='{host}' user='{user}' port='{port}'", status=500)


def register(request):
    if request.user.is_authenticated:
        next_url = request.GET.get('next', 'dashboard')
        return redirect(next_url)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'register.html')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, 'Account created successfully!')
        next_url = request.GET.get('next') or request.POST.get('next', 'dashboard')
        return redirect(next_url)
    
    return render(request, 'register.html')


def login_view(request):
    if request.user.is_authenticated:
        next_url = request.GET.get('next', 'dashboard')
        return redirect(next_url)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return render(request, 'login.html')
        
        # Try to find user by email
        try:
            user_obj = User.objects.get(email=email)
            # Authenticate using the username
            user = authenticate(request, username=user_obj.username, password=password)
            
            if user is None:
                # Try authenticating with email directly as some backends support it
                user = authenticate(request, email=email, password=password)
                
        except User.DoesNotExist:
            user = None
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next') or request.POST.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
            return render(request, 'login.html')
    
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('main:home')


def order_payment_proof(request, order_id):
    """Customer submits payment proof for their order."""
    order = get_object_or_404(Order, id=order_id)
    
    if order.status not in ['pending', 'payment_submitted']:
        return HttpResponse("This order is already processed.", status=400)
    
    if request.method == 'POST':
        form = PaymentProofForm(request.POST)
        if form.is_valid():
            order.payment_proof = form.cleaned_data['payment_proof']
            order.payment_proof_image = form.cleaned_data.get('payment_proof_image', '')
            order.status = 'payment_submitted'
            order.payment_submitted_at = timezone.now()
            order.save()
            
            # Notify admin
            if settings.ADMIN_EMAIL:
                subject = f'Payment Proof Submitted - Order #{order.id}'
                body = f"""Order #{order.id} payment proof submitted:

Customer: {order.name}
Email: {order.email}
Vehicle: {order.vehicle}
Payment Proof: {order.payment_proof}
Screenshot: {order.payment_proof_image or 'Not provided'}

Please review and approve in admin panel.
"""
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])
            
            # Confirm to customer
            if order.email:
                send_mail(
                    'Payment Proof Received',
                    f'Thank you {order.name}, we received your payment proof. We will verify and confirm shortly.',
                    settings.DEFAULT_FROM_EMAIL,
                    [order.email]
                )
            
            return render(request, 'payment_proof_success.html', {'order': order})
    else:
        form = PaymentProofForm()
    
    return render(request, 'payment_proof.html', {'order': order, 'form': form})
