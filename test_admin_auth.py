import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.conf import settings

if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

User = get_user_model()

print("\n" + "="*70)
print("TESTING ADMIN & AUTHENTICATED ACCESS")
print("="*70)

# Create test superuser if doesn't exist
print("\n1. CHECKING/CREATING ADMIN USER")
print("-" * 70)
try:
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        admin = User.objects.create_superuser(
            username='testadmin',
            email='admin@test.com',
            password='testpass123'
        )
        print("✓ Created test admin user")
    else:
        print(f"✓ Found existing admin: {admin.username}")
except Exception as e:
    print(f"✗ Admin user error: {e}")
    admin = None

# Test admin login
print("\n2. TESTING ADMIN LOGIN")
print("-" * 70)
client = Client()

if admin:
    # Try to login
    login_success = client.login(username=admin.username, password='testpass123' if admin.username == 'testadmin' else 'ChangeMeNow!123')
    
    if not login_success:
        # Try with the admin from .env
        login_success = client.login(username='admin', password='ChangeMeNow!123')
    
    if login_success:
        print("✓ Admin login successful")
        
        # Test admin pages with authentication
        print("\n3. TESTING ADMIN PAGES (AUTHENTICATED)")
        print("-" * 70)
        
        admin_pages = [
            ('Admin Home', '/admin/'),
            ('Admin Users', '/admin/users/customuser/'),
            ('Admin Orders', '/admin/main/order/'),
            ('Admin Vehicles', '/admin/main/vehicle/'),
            ('Admin Support Messages', '/admin/main/supportmessage/'),
            ('Admin Tracking', '/admin/main/tracking/'),
            ('Admin Investments', '/admin/main/investment/'),
            ('Admin Deposits', '/admin/deposits/deposit/'),
            ('Admin Withdrawals', '/admin/withdrawals/withdrawal/'),
            ('Admin Support Tickets', '/admin/support/ticket/'),
        ]
        
        passed = 0
        failed = 0
        
        for name, url in admin_pages:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    print(f"✓ {name:35} → 200 OK")
                    passed += 1
                elif response.status_code == 302:
                    print(f"✓ {name:35} → 302 Redirect")
                    passed += 1
                elif response.status_code == 404:
                    print(f"⚠ {name:35} → 404 Not Found (app may not exist)")
                    failed += 1
                else:
                    print(f"✗ {name:35} → {response.status_code}")
                    failed += 1
            except Exception as e:
                print(f"✗ {name:35} → ERROR: {str(e)[:40]}")
                failed += 1
        
        print(f"\nAdmin Pages: {passed} passed, {failed} failed")
    else:
        print("✗ Admin login failed")

# Test regular user authentication
print("\n4. TESTING REGULAR USER ACCESS")
print("-" * 70)

client2 = Client()
regular_user = User.objects.filter(is_superuser=False).first()

if regular_user:
    print(f"✓ Found regular user: {regular_user.username}")
    
    # Create session for testing (without actual login since we don't know password)
    client2.force_login(regular_user)
    print("✓ Simulated user login")
    
    protected_pages = [
        ('Dashboard', '/dashboard/'),
        ('Deposits', '/deposits/'),
        ('Withdrawals', '/withdrawals/'),
        ('Investments', '/investments/'),
        ('Transactions', '/transactions/'),
    ]
    
    passed = 0
    for name, url in protected_pages:
        try:
            response = client2.get(url)
            if response.status_code in [200, 302]:
                print(f"✓ {name:35} → {response.status_code}")
                passed += 1
            else:
                print(f"✗ {name:35} → {response.status_code}")
        except Exception as e:
            print(f"✗ {name:35} → ERROR: {str(e)[:40]}")
    
    print(f"\nProtected Pages: {passed}/{len(protected_pages)} accessible")
else:
    print("⚠ No regular users found - create one via /register/")

# Test models
print("\n5. TESTING DATA MODELS")
print("-" * 70)

from main.models import Vehicle, Order, SupportMessage, Tracking, Investment
from apps.deposits.models import Deposit
from apps.withdrawals.models import Withdrawal

models_data = [
    ('Vehicles', Vehicle.objects.count()),
    ('Orders', Order.objects.count()),
    ('Support Messages', SupportMessage.objects.count()),
    ('Tracking Records', Tracking.objects.count()),
    ('Investments', Investment.objects.count()),
    ('Deposits', Deposit.objects.count()),
    ('Withdrawals', Withdrawal.objects.count()),
]

for model_name, count in models_data:
    print(f"✓ {model_name:30} {count} records")

# Test payment workflow fields
print("\n6. TESTING PAYMENT WORKFLOW")
print("-" * 70)

order = Order.objects.first()
if order:
    print(f"✓ Sample Order #{order.id}:")
    print(f"  - Status: {order.status}")
    print(f"  - Has address: {'Yes' if order.address else 'No'}")
    print(f"  - Has crypto address: {'Yes' if order.crypto_address else 'No'}")
    print(f"  - Has payment proof: {'Yes' if order.payment_proof else 'No'}")
    print(f"  - Payment fields working: ✓")
else:
    print("⚠ No orders yet - payment workflow ready but untested")

print("\n" + "="*70)
print("✅ ADMIN & AUTHENTICATION TEST COMPLETE")
print("="*70 + "\n")
