import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.conf import settings

# Add testserver to ALLOWED_HOSTS for testing
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

client = Client()

pages = [
    ('Home', '/'),
    ('Vehicles', '/vehicles/'),
    ('Buy Vehicle #1', '/buy/1/'),
    ('Support', '/support/'),
    ('Track', '/track/'),
    ('Invest', '/invest/'),
    ('Register', '/register/'),
    ('Login', '/login/'),
    ('Email Debug', '/email-debug/'),
    ('Email Test', '/email-test/'),
    ('Admin Login', '/admin/'),
    ('Admin Orders', '/admin/main/order/'),
]

print("\n" + "="*70)
print("TESTING ALL PAGES")
print("="*70 + "\n")

passed = 0
failed = 0

for name, url in pages:
    try:
        response = client.get(url)
        status = response.status_code
        
        # 200 = OK, 302 = redirect (ok for login pages), 405 = method not allowed (expected for some)
        if status in [200, 302]:
            print(f"✓ {name:30} → {status}")
            passed += 1
        elif status == 405:
            print(f"✓ {name:30} → {status} (POST only, but page exists)")
            passed += 1
        else:
            print(f"✗ {name:30} → {status}")
            failed += 1
    except Exception as e:
        print(f"✗ {name:30} → ERROR: {e}")
        failed += 1

print("\n" + "="*70)
print(f"Results: {passed} ✓ PASS | {failed} ✗ FAIL")
print("="*70 + "\n")

if failed == 0:
    print("✅ ALL PAGES WORKING!")
else:
    print(f"⚠ {failed} page(s) have issues")
