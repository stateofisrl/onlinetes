#!/usr/bin/env python
"""
Test script to send all order-related emails to a test email address.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from main.models import Vehicle, Order, Tracking
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

TEST_EMAIL = 'noobodii6@gmail.com'
TEST_NAME = 'Test Customer'

print("="*60)
print("TESTING ORDER EMAIL TEMPLATES")
print("="*60)
print(f"\nSending test emails to: {TEST_EMAIL}\n")

# Get or create a test vehicle
vehicle = Vehicle.objects.first()
if not vehicle:
    print("❌ No vehicles found. Please add a vehicle first.")
    sys.exit(1)

print(f"Using vehicle: {vehicle.name}\n")

# Test 1: Order Confirmation Email
print("1️⃣  Testing ORDER CONFIRMATION email...")
print("-" * 60)

order = Order.objects.create(
    vehicle=vehicle,
    name=TEST_NAME,
    email=TEST_EMAIL,
    phone='+1234567890',
    address='123 Test Street, Test City, TC 12345',
    status='pending'
)
print(f"✓ Created order #{order.id}")

# Manually send order confirmation (simulating what happens in views.py)
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
send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [TEST_EMAIL], html_message=html_message, fail_silently=False)
print(f"✓ Order confirmation email sent to {TEST_EMAIL}")

# Test 2: Payment Details Email
print("\n2️⃣  Testing PAYMENT DETAILS email...")
print("-" * 60)

order.crypto_address = 'TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE'
order.crypto_currency = 'USDT (TRC20)'
order.payment_amount = vehicle.price_usd
order.save()
print(f"✓ Set payment details for order #{order.id}")

# Manually send payment details email
subject = f'Payment Details for Order #{order.id} - Tesla Investment Platform'
html_message = f"""
<html>
<body style="font-family: Arial, sans-serif; background-color: #000; color: #fff; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #1a1a1a; border: 1px solid #333; padding: 30px; border-radius: 8px;">
        <h2 style="color: #fff; margin-bottom: 20px;">Payment Details Ready</h2>
        <p style="color: #ccc; line-height: 1.6;">Hi {order.name},</p>
        <p style="color: #ccc; line-height: 1.6;">
            Thank you for ordering <strong style="color: #fff;">{vehicle.name}</strong>!
        </p>
        <p style="color: #ccc; line-height: 1.6;">
            Please send payment to complete your order:
        </p>
        <div style="background-color: #222; padding: 20px; border-radius: 6px; margin: 20px 0;">
            <p style="color: #999; margin: 5px 0;">Order ID: <strong style="color: #fff;">#{order.id}</strong></p>
            <p style="color: #999; margin: 5px 0;">Amount: <strong style="color: #4ade80;">${order.payment_amount} USD</strong></p>
            <p style="color: #999; margin: 5px 0;">Currency: <strong style="color: #fff;">{order.crypto_currency}</strong></p>
            <p style="color: #999; margin: 10px 0 5px 0;">Payment Address:</p>
            <code style="background-color: #000; color: #4ade80; padding: 10px; display: block; border-radius: 4px; word-break: break-all; font-size: 14px;">{order.crypto_address}</code>
        </div>
        <div style="background-color: #1a1a1a; border: 1px solid #333; padding: 15px; border-radius: 6px; margin: 20px 0;">
            <p style="color: #999; margin: 5px 0; font-size: 14px;">Delivery Address:</p>
            <p style="color: #fff; margin: 5px 0;">{order.address}</p>
        </div>
        <p style="color: #4ade80; line-height: 1.6; margin-top: 20px;">✓ After making payment, submit your transaction proof:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="http://127.0.0.1:8001/order/{order.id}/payment/" style="background-color: #fff; color: #000; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                Submit Payment Proof
            </a>
        </div>
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #333;">
            <p style="color: #666; font-size: 12px; margin: 0;">Best regards,</p>
            <p style="color: #666; font-size: 12px; margin: 0;">Tesla Investment Platform Team</p>
        </div>
    </div>
</body>
</html>
"""

plain_message = strip_tags(html_message)
send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [TEST_EMAIL], html_message=html_message, fail_silently=False)
print(f"✓ Payment details email sent to {TEST_EMAIL}")

# Test 3: Payment Approved / Tracking Email
print("\n3️⃣  Testing PAYMENT APPROVED / TRACKING email...")
print("-" * 60)

order.status = 'payment_approved'
order.payment_approved_at = timezone.now()
order.save()

import random
tracking, created = Tracking.objects.get_or_create(
    order=order,
    defaults={
        'tracking_id': f'TRK{random.randint(100000, 999999)}',
        'vehicle': order.vehicle,
        'customer_name': order.name,
        'status': 'Order confirmed',
        'to_location': order.address,
    }
)
print(f"✓ Created tracking #{tracking.tracking_id}")

# Manually send payment approved email
subject = f'Payment Approved - Tesla Investment Platform'
html_message = f"""
<html>
<body style="font-family: Arial, sans-serif; background-color: #000; color: #fff; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #1a1a1a; border: 1px solid #333; padding: 30px; border-radius: 8px;">
        <h2 style="color: #fff; margin-bottom: 20px;">Payment Approved! 🎉</h2>
        <p style="color: #ccc; line-height: 1.6;">Hi {order.name},</p>
        <p style="color: #ccc; line-height: 1.6;">
            Great news! Your payment has been <strong style="color: #4ade80;">approved</strong> and your order is now being processed.
        </p>
        <div style="background-color: #222; padding: 20px; border-radius: 6px; margin: 20px 0;">
            <p style="color: #999; margin: 5px 0;">Tracking ID: <strong style="color: #4ade80;">{tracking.tracking_id}</strong></p>
            <p style="color: #999; margin: 5px 0;">Vehicle: <strong style="color: #fff;">{order.vehicle.name}</strong></p>
            <p style="color: #999; margin: 5px 0;">Status: <strong style="color: #4ade80;">{tracking.status}</strong></p>
            <p style="color: #999; margin: 5px 0;">Delivery Address: <strong style="color: #fff;">{order.address}</strong></p>
        </div>
        <p style="color: #4ade80; line-height: 1.6;">✓ You can track your order anytime using the link below:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="http://127.0.0.1:8001/track/?tracking_id={tracking.tracking_id}" style="background-color: #fff; color: #000; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                Track Your Order
            </a>
        </div>
        <p style="color: #ccc; font-size: 14px; margin-top: 20px;">We'll keep you updated on your order status. If you have any questions, please contact our support team.</p>
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #333;">
            <p style="color: #666; font-size: 12px; margin: 0;">Best regards,</p>
            <p style="color: #666; font-size: 12px; margin: 0;">Tesla Investment Platform Team</p>
        </div>
    </div>
</body>
</html>
"""

plain_message = strip_tags(html_message)
send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [TEST_EMAIL], html_message=html_message, fail_silently=False)
print(f"✓ Payment approved/tracking email sent to {TEST_EMAIL}")

print("\n" + "="*60)
print("✅ ALL TEST EMAILS SENT SUCCESSFULLY!")
print("="*60)
print(f"\nCheck {TEST_EMAIL} for:")
print("  1. Order Confirmation")
print("  2. Payment Details")
print("  3. Payment Approved / Tracking")
print("\nTest order ID:", order.id)
print("Tracking ID:", tracking.tracking_id)
print("="*60)
