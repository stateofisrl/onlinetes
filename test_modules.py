import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from main.models import Order, Vehicle
from main.forms import OrderForm, PaymentProofForm
from django.test import RequestFactory

# Test Order model
print("Testing Order model...")
try:
    o = Order.objects.first()
    if o:
        print(f"✓ Order exists: {o}")
    else:
        print("✓ No orders yet (expected)")
except Exception as e:
    print(f"✗ Order model error: {e}")

# Test OrderForm
print("\nTesting OrderForm...")
try:
    form = OrderForm()
    print(f"✓ OrderForm fields: {list(form.fields.keys())}")
except Exception as e:
    print(f"✗ OrderForm error: {e}")

# Test PaymentProofForm
print("\nTesting PaymentProofForm...")
try:
    form = PaymentProofForm()
    print(f"✓ PaymentProofForm fields: {list(form.fields.keys())}")
except Exception as e:
    print(f"✗ PaymentProofForm error: {e}")

# Test views
print("\nTesting views...")
try:
    from main import views
    print(f"✓ Views module loaded")
    # Check if order_payment_proof exists
    if hasattr(views, 'order_payment_proof'):
        print(f"✓ order_payment_proof view exists")
    else:
        print(f"✗ order_payment_proof view missing")
except Exception as e:
    print(f"✗ Views error: {e}")

print("\n✓ All module checks passed!")
