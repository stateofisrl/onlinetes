#!/usr/bin/env python
"""
Test referral API endpoints
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from apps.referrals.models import Referral, ReferralSettings, ReferralCommission
from apps.deposits.models import Deposit

User = get_user_model()
client = Client()

print("=" * 60)
print("TESTING REFERRAL SYSTEM")
print("=" * 60)

# 1. Check if users exist
print("\n1. Checking users...")
users = User.objects.all()
print(f"Total users: {users.count()}")
for u in users[:5]:
    print(f"   - {u.username} (referral_code: {u.referral_code})")

# 2. Check referrals
print("\n2. Checking referrals...")
referrals = Referral.objects.all()
print(f"Total referrals: {referrals.count()}")
for ref in referrals:
    print(f"   - {ref.referrer.username} → {ref.referred.username}")

# 3. Check commissions
print("\n3. Checking commissions...")
commissions = ReferralCommission.objects.all()
print(f"Total commissions: {commissions.count()}")
for com in commissions[:5]:
    print(f"   - {com.referral.referrer.username}: ${com.amount} ({com.status})")

# 4. Check referral settings
print("\n4. Checking referral settings...")
settings = ReferralSettings.objects.first()
if settings:
    print(f"   Commission rate: {settings.commission_percentage}%")
    print(f"   Is active: {settings.is_active}")
else:
    print("   No referral settings found!")

# 5. Test API endpoint with a user
print("\n5. Testing API endpoints...")
if users.count() > 0:
    user = users.first()
    print(f"\nTesting with user: {user.username}")
    
    # Login
    login_success = client.login(username=user.username, password='testpass123')
    print(f"   Login successful: {login_success}")
    
    if login_success:
        # Test stats endpoint
        response = client.get('/api/referrals/stats/')
        print(f"   GET /api/referrals/stats/: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"      Stats: {json.dumps(data, indent=2)}")
        
        # Test my_referrals endpoint
        response = client.get('/api/referrals/my_referrals/')
        print(f"   GET /api/referrals/my_referrals/: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"      Data: {json.dumps(data, indent=2)}")

print("\n" + "=" * 60)
