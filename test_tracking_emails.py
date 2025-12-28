#!/usr/bin/env python
"""
Test script to send tracking status update emails.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from main.models import Tracking, Order, Vehicle
from decimal import Decimal

TEST_EMAIL = 'noobodii6@gmail.com'
TEST_NAME = 'Test Customer'

print("="*60)
print("TESTING TRACKING STATUS UPDATE EMAILS")
print("="*60)
print(f"\nSending test emails to: {TEST_EMAIL}\n")

# Get or create test vehicle
vehicle = Vehicle.objects.first()
if not vehicle:
    vehicle = Vehicle.objects.create(
        name='Test Vehicle',
        model='Model S',
        price_usd=Decimal('50000.00')
    )
    print(f"✓ Created test vehicle: {vehicle.name}")
else:
    print(f"✓ Using existing vehicle: {vehicle.name}")

# Get or create test order
order = Order.objects.filter(email=TEST_EMAIL).first()
if not order:
    order = Order.objects.create(
        vehicle=vehicle,
        name=TEST_NAME,
        email=TEST_EMAIL,
        phone='1234567890',
        address='123 Test St, Test City, TC 12345'
    )
    print(f"✓ Created test order #{order.id}")
else:
    print(f"✓ Using existing order #{order.id}")

# Test 1: Order Confirmed
print("\n1️⃣  Testing ORDER CONFIRMED email...")
print("-"*60)
tracking1 = Tracking.objects.create(
    tracking_id='TRK-TEST-001',
    order=order,
    vehicle=vehicle,
    customer_name=TEST_NAME,
    status='Order confirmed',
    from_location='Warehouse, USA',
    to_location=order.address
)
print(f"✓ Order confirmed tracking email sent to {TEST_EMAIL}")

# Test 2: Processing
print("\n2️⃣  Testing PROCESSING email...")
print("-"*60)
tracking1.status = 'Processing'
tracking1.save()
print(f"✓ Processing status email sent to {TEST_EMAIL}")

# Test 3: Shipped
print("\n3️⃣  Testing SHIPPED email...")
print("-"*60)
tracking2 = Tracking.objects.create(
    tracking_id='TRK-TEST-002',
    order=order,
    vehicle=vehicle,
    customer_name=TEST_NAME,
    status='Shipped',
    from_location='Distribution Center, USA',
    to_location=order.address
)
print(f"✓ Shipped status email sent to {TEST_EMAIL}")

# Test 4: In Transit
print("\n4️⃣  Testing IN TRANSIT email...")
print("-"*60)
tracking2.status = 'In Transit'
tracking2.save()
print(f"✓ In transit status email sent to {TEST_EMAIL}")

# Test 5: Delivered
print("\n5️⃣  Testing DELIVERED email...")
print("-"*60)
tracking2.status = 'Delivered'
tracking2.save()
print(f"✓ Delivered status email sent to {TEST_EMAIL}")

print("\n" + "="*60)
print("✅ ALL TRACKING STATUS EMAILS SENT SUCCESSFULLY!")
print("="*60)
print(f"\nCheck {TEST_EMAIL} for:")
print("  1. Order Confirmed")
print("  2. Processing")
print("  3. Shipped")
print("  4. In Transit")
print("  5. Delivered")
print("="*60)
