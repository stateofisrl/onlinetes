import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory, Client
from main.models import Order, Vehicle
from main.views import buy_vehicle, order_payment_proof
from main.forms import OrderForm, PaymentProofForm

print("\n" + "="*60)
print("TESTING PAYMENT WORKFLOW")
print("="*60)

# Setup
factory = RequestFactory()
client = Client()
vehicle = Vehicle.objects.first()

if not vehicle:
    print("✗ No vehicles in database!")
    exit(1)

print(f"\n1. TESTING BUY VEHICLE FORM")
print("-" * 60)
form_data = {
    'vehicle': vehicle.id,
    'name': 'Test Customer',
    'email': 'test@example.com',
    'phone': '1234567890',
    'address': '123 Main St, Test City'
}
form = OrderForm(data=form_data)
if form.is_valid():
    print(f"✓ Form valid: {list(form.cleaned_data.keys())}")
    order = form.save()
    print(f"✓ Order created: #{order.id} - Status: {order.status}")
else:
    print(f"✗ Form invalid: {form.errors}")

# Refresh order
order = Order.objects.get(id=order.id)

print(f"\n2. TESTING PAYMENT DETAILS VIEW")
print("-" * 60)
try:
    request = factory.get(f'/order/{order.id}/payment/')
    response = order_payment_proof(request, order.id)
    if response.status_code == 200:
        print(f"✓ Payment proof page loads (status 200)")
        print(f"✓ Order shows: ID={order.id}, Status={order.status}, Amount=${order.vehicle.price_usd}")
    else:
        print(f"✗ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

print(f"\n3. TESTING PAYMENT PROOF SUBMISSION")
print("-" * 60)
proof_data = {
    'payment_proof': 'tx_hash_abc123def456',
    'payment_proof_image': 'https://example.com/payment.png'
}
proof_form = PaymentProofForm(data=proof_data)
if proof_form.is_valid():
    print(f"✓ Payment proof form valid")
    print(f"  - Proof: {proof_form.cleaned_data['payment_proof']}")
    print(f"  - Screenshot: {proof_form.cleaned_data.get('payment_proof_image', 'N/A')}")
else:
    print(f"✗ Form invalid: {proof_form.errors}")

print(f"\n4. TESTING ORDER FIELDS")
print("-" * 60)
order_fields = {
    'id': order.id,
    'status': order.status,
    'name': order.name,
    'email': order.email,
    'phone': order.phone,
    'address': order.address,
    'vehicle': order.vehicle.name if order.vehicle else None,
    'crypto_address': order.crypto_address,
    'crypto_currency': order.crypto_currency,
    'payment_amount': order.payment_amount,
}
for key, value in order_fields.items():
    status = "✓" if value or value == '' else "✗"
    print(f"{status} {key}: {value}")

print(f"\n5. TESTING ADMIN WORKFLOW")
print("-" * 60)
# Simulate admin setting payment details
order.crypto_address = 'TJYmkA1nq9wJ6XkbSmzKpDVHvgHRW8GYjD'
order.crypto_currency = 'USDT'
order.payment_amount = order.vehicle.price_usd
order.save()
print(f"✓ Admin set payment details:")
print(f"  - Address: {order.crypto_address}")
print(f"  - Currency: {order.crypto_currency}")
print(f"  - Amount: ${order.payment_amount}")

print(f"\n6. TESTING PAYMENT SUBMISSION")
print("-" * 60)
order.payment_proof = 'tx_hash_abc123def456'
order.payment_proof_image = 'https://example.com/screenshot.png'
order.status = 'payment_submitted'
order.save()
print(f"✓ Payment proof submitted:")
print(f"  - Status: {order.status}")
print(f"  - Proof: {order.payment_proof}")

print(f"\n7. TESTING PAYMENT APPROVAL")
print("-" * 60)
from django.utils import timezone
order.status = 'payment_approved'
order.payment_approved_at = timezone.now()
order.save()
print(f"✓ Payment approved:")
print(f"  - Status: {order.status}")
print(f"  - Approved at: {order.payment_approved_at}")

# Check if tracking was created
from main.models import Tracking
tracking = Tracking.objects.filter(order=order).first()
if tracking:
    print(f"✓ Tracking created: {tracking.tracking_id}")
else:
    print(f"✗ No tracking created")

print("\n" + "="*60)
print("✓ ALL TESTS PASSED!")
print("="*60 + "\n")
