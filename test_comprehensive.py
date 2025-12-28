import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.conf import settings
from django.contrib.auth import get_user_model

# Add testserver to ALLOWED_HOSTS for testing
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

User = get_user_model()
client = Client()

print("\n" + "="*70)
print("COMPREHENSIVE SYSTEM TEST")
print("="*70 + "\n")

# Test all main features
tests = {
    'Authentication & User Management': [
        ('Login Page', '/login/', 'GET'),
        ('Register Page', '/register/', 'GET'),
        ('Logout', '/logout/', 'GET'),
    ],
    'Investment Platform Pages': [
        ('Dashboard', '/dashboard/', 'GET'),
        ('Deposits Page', '/deposits/', 'GET'),
        ('Withdrawals Page', '/withdrawals/', 'GET'),
        ('Investments Page', '/investments/', 'GET'),
        ('Support Page (Platform)', '/support/', 'GET'),
        ('Transactions', '/transactions/', 'GET'),
        ('Referrals', '/referrals/', 'GET'),
    ],
    'Tesla Site Pages': [
        ('Home', '/', 'GET'),
        ('Vehicles', '/vehicles/', 'GET'),
        ('Buy Vehicle', '/buy/1/', 'GET'),
        ('Support (Tesla)', '/support/', 'GET'),
        ('Track Order', '/track/', 'GET'),
        ('Invest', '/invest/', 'GET'),
    ],
    'Admin Interface': [
        ('Admin Home', '/admin/', 'GET'),
        ('Admin Users', '/admin/users/customuser/', 'GET'),
        ('Admin Orders', '/admin/main/order/', 'GET'),
        ('Admin Vehicles', '/admin/main/vehicle/', 'GET'),
        ('Admin Support', '/admin/main/supportmessage/', 'GET'),
        ('Admin Tracking', '/admin/main/tracking/', 'GET'),
        ('Admin Investments', '/admin/main/investment/', 'GET'),
        ('Admin Deposits', '/admin/deposits/deposit/', 'GET'),
        ('Admin Withdrawals', '/admin/withdrawals/withdrawal/', 'GET'),
    ],
    'Email & Diagnostics': [
        ('Email Debug', '/email-debug/', 'GET'),
        ('Email Test', '/email-test/', 'GET'),
    ],
}

total_pass = 0
total_fail = 0
results = {}

for category, pages in tests.items():
    print(f"\n{category}")
    print("-" * 70)
    category_pass = 0
    category_fail = 0
    
    for name, url, method in pages:
        try:
            if method == 'GET':
                response = client.get(url)
            else:
                response = client.post(url)
            
            status = response.status_code
            
            # Success statuses
            if status == 200:
                print(f"✓ {name:35} → {status} OK")
                category_pass += 1
            elif status == 302:
                print(f"✓ {name:35} → {status} Redirect (auth required)")
                category_pass += 1
            elif status == 301:
                print(f"✓ {name:35} → {status} Permanent redirect")
                category_pass += 1
            elif status == 404:
                print(f"⚠ {name:35} → {status} Not Found")
                category_fail += 1
            else:
                print(f"✗ {name:35} → {status}")
                category_fail += 1
                
        except Exception as e:
            print(f"✗ {name:35} → ERROR: {str(e)[:50]}")
            category_fail += 1
    
    results[category] = (category_pass, category_fail)
    total_pass += category_pass
    total_fail += category_fail

# Print summary
print("\n" + "="*70)
print("SUMMARY BY CATEGORY")
print("="*70)

for category, (passed, failed) in results.items():
    total = passed + failed
    status = "✅" if failed == 0 else "⚠️" if passed > failed else "❌"
    print(f"{status} {category:40} {passed}/{total} passed")

print("\n" + "="*70)
print(f"OVERALL: {total_pass} ✓ PASS | {total_fail} ✗ FAIL")
print("="*70)

# Test user creation
print("\n" + "="*70)
print("TESTING USER MODELS")
print("="*70)

try:
    user_count = User.objects.count()
    print(f"✓ Total users in database: {user_count}")
    
    if user_count > 0:
        user = User.objects.first()
        print(f"✓ Sample user: {user.username} ({user.email})")
        print(f"  - Is staff: {user.is_staff}")
        print(f"  - Is superuser: {user.is_superuser}")
except Exception as e:
    print(f"✗ User model error: {e}")

# Test admin settings
print("\n" + "="*70)
print("TESTING DJANGO SETTINGS")
print("="*70)

critical_settings = [
    ('DEBUG', settings.DEBUG),
    ('SECRET_KEY', '***' if settings.SECRET_KEY else None),
    ('ALLOWED_HOSTS', settings.ALLOWED_HOSTS),
    ('DATABASE_ENGINE', settings.DATABASES['default']['ENGINE']),
    ('EMAIL_BACKEND', settings.EMAIL_BACKEND),
    ('EMAIL_HOST', settings.EMAIL_HOST),
    ('EMAIL_HOST_USER', settings.EMAIL_HOST_USER or 'Not set'),
    ('DEFAULT_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL),
    ('ADMIN_EMAIL', getattr(settings, 'ADMIN_EMAIL', 'Not set')),
    ('STATIC_URL', settings.STATIC_URL),
    ('MEDIA_URL', settings.MEDIA_URL),
]

for setting_name, value in critical_settings:
    if value:
        print(f"✓ {setting_name:25} = {value}")
    else:
        print(f"⚠ {setting_name:25} = Not configured")

# Test installed apps
print("\n" + "="*70)
print("INSTALLED APPS")
print("="*70)

for app in settings.INSTALLED_APPS:
    if not app.startswith('django.'):
        print(f"✓ {app}")

print("\n" + "="*70)
if total_fail == 0:
    print("✅ ALL SYSTEMS OPERATIONAL!")
else:
    print(f"⚠️ {total_fail} ISSUES FOUND - Review above for details")
print("="*70 + "\n")
