#!/usr/bin/env python
"""Create a user referred by penjen"""
import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.referrals.models import Referral

User = get_user_model()

# Get penjen
penjen = User.objects.get(referral_code='2E91EF77')
print(f"Referrer: {penjen.username}")

# Create a new user
new_email = f"referred_{uuid.uuid4().hex[:8]}@example.com"
new_user = User.objects.create_user(
    email=new_email,
    username=new_email,
    password='testpass123'
)

print(f"Created user: {new_user.username}")

# Create the referral relationship
referral = Referral.objects.create(
    referrer=penjen,
    referred=new_user
)

print(f"✓ Referral created: {penjen.username} → {new_user.username}")

# Verify
penjen_referrals = Referral.objects.filter(referrer=penjen)
print(f"\n{penjen.username} now has {penjen_referrals.count()} referral(s)")
for ref in penjen_referrals:
    print(f"  - {ref.referred.username} ({ref.referred.email})")
