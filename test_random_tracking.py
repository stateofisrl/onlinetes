#!/usr/bin/env python
"""
Test script to send payment approved email with random tracking ID.
"""
import os
import sys
import django
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from main.models import Vehicle, Order, Tracking
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.html import strip_tags

TEST_EMAIL = 'noobodii6@gmail.com'
TEST_NAME = 'Test Customer'

print("="*60)
print("TESTING RANDOM TRACKING ID")
print("="*60)

# Get or create a test vehicle
vehicle = Vehicle.objects.first()
if not vehicle:
    print("❌ No vehicles found. Please add a vehicle first.")
    sys.exit(1)

print(f"\nUsing vehicle: {vehicle.name}\n")

# Create order
order = Order.objects.create(
    vehicle=vehicle,
    name=TEST_NAME,
    email=TEST_EMAIL,
    phone='+1234567890',
    address='123 Test Street, Test City, TC 12345',
    status='pending'
)
print(f"✓ Created order #{order.id}")

# Set payment details
order.crypto_address = 'TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE'
order.crypto_currency = 'USDT (TRC20)'
order.payment_amount = vehicle.price_usd
order.status = 'payment_approved'
order.payment_approved_at = timezone.now()
order.save()

# Create tracking with RANDOM ID
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
print(f"✓ Created tracking: {tracking.tracking_id} (RANDOM)")

# Send payment approved email
subject = f'Payment Approved - Tesla Investment Platform'
html_message = f"""
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #000; color: #fff; padding: 20px; margin: 0;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #1a1a1a; border: 1px solid #333; border-radius: 8px; overflow: hidden;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%); padding: 30px 20px; text-align: center; border-bottom: 2px solid #4ade80;">
            <h1 style="color: #4ade80; margin: 0; font-size: 28px;">Payment Approved! 🎉</h1>
        </div>
        
        <!-- Main Content -->
        <div style="padding: 30px 20px;">
            <p style="color: #ccc; line-height: 1.8; margin: 0 0 20px 0; font-size: 16px;">Hi {order.name},</p>
            
            <p style="color: #ccc; line-height: 1.8; margin: 0 0 20px 0;">
                Great news! Your payment has been <strong style="color: #4ade80;">successfully approved</strong> and your order is now being processed and prepared for shipment.
            </p>
            
            <!-- Order Details Card -->
            <div style="background-color: #222; padding: 20px; border-left: 4px solid #4ade80; margin: 20px 0; border-radius: 4px;">
                <h3 style="color: #4ade80; margin-top: 0; margin-bottom: 15px; font-size: 18px;">Order & Tracking Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="color: #999; padding: 8px 0; border-bottom: 1px solid #333;">Order ID:</td>
                        <td style="color: #fff; padding: 8px 0; border-bottom: 1px solid #333; text-align: right;"><strong>#{order.id}</strong></td>
                    </tr>
                    <tr>
                        <td style="color: #999; padding: 8px 0; border-bottom: 1px solid #333;">Tracking ID:</td>
                        <td style="color: #4ade80; padding: 8px 0; border-bottom: 1px solid #333; text-align: right;"><strong>{tracking.tracking_id}</strong></td>
                    </tr>
                    <tr>
                        <td style="color: #999; padding: 8px 0; border-bottom: 1px solid #333;">Vehicle:</td>
                        <td style="color: #fff; padding: 8px 0; border-bottom: 1px solid #333; text-align: right;"><strong>{order.vehicle.name}</strong></td>
                    </tr>
                    <tr>
                        <td style="color: #999; padding: 8px 0; border-bottom: 1px solid #333;">Status:</td>
                        <td style="color: #4ade80; padding: 8px 0; border-bottom: 1px solid #333; text-align: right;"><strong>{tracking.status}</strong></td>
                    </tr>
                    <tr>
                        <td style="color: #999; padding: 8px 0;">Delivery Address:</td>
                        <td style="color: #fff; padding: 8px 0; text-align: right;"><strong>{order.address}</strong></td>
                    </tr>
                </table>
            </div>
            
            <!-- Track Order CTA -->
            <div style="text-align: center; margin: 30px 0;">
                <p style="color: #4ade80; font-size: 14px; margin: 0 0 15px 0;">✓ Track your order in real-time</p>
                <a href="{settings.SITE_URL}/track/?tracking_id={tracking.tracking_id}" style="background-color: #4ade80; color: #000; padding: 14px 40px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 16px; transition: background-color 0.3s;">
                    Track Your Order
                </a>
            </div>
            
            <!-- Additional Info -->
            <div style="background-color: #1a1a1a; padding: 15px; border-radius: 4px; margin: 20px 0;">
                <p style="color: #999; font-size: 14px; margin: 0 0 10px 0;"><strong>What's Next?</strong></p>
                <ul style="color: #999; font-size: 14px; margin: 0; padding-left: 20px;">
                    <li style="margin-bottom: 5px;">Your vehicle will be verified and prepared</li>
                    <li style="margin-bottom: 5px;">We'll arrange the best shipping method</li>
                    <li style="margin-bottom: 5px;">You'll receive tracking updates via email</li>
                    <li>Estimated delivery time will be confirmed shortly</li>
                </ul>
            </div>
            
            <p style="color: #ccc; font-size: 14px; margin-top: 20px; line-height: 1.6;">We'll keep you updated on your order status throughout the delivery process. If you have any questions or concerns, please don't hesitate to contact our support team.</p>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #111; padding: 20px; text-align: center; border-top: 1px solid #333;">
            <p style="color: #666; font-size: 12px; margin: 0 0 10px 0;">Best regards,</p>
            <p style="color: #4ade80; font-size: 13px; font-weight: bold; margin: 0;">Tesla Investment Platform Team</p>
            <p style="color: #666; font-size: 11px; margin: 10px 0 0 0;">© 2025 Tesla Investment Platform. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

plain_message = strip_tags(html_message)
send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [TEST_EMAIL], html_message=html_message, fail_silently=False)
print(f"✓ Email sent to {TEST_EMAIL}")

print("\n" + "="*60)
print("✅ TEST COMPLETE!")
print("="*60)
print(f"\nTracker ID sent: {tracking.tracking_id}")
print(f"Email: {TEST_EMAIL}")
print("="*60)
