#!/usr/bin/env python
"""Create test referral data"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.referrals.models import Referral, ReferralCommission
from apps.deposits.models import Deposit

User = get_user_model()

# Get users
users = list(User.objects.all())

if len(users) >= 2:
    referrer = users[0]
    referred = users[1]
    
    # Create referral
    referral, created = Referral.objects.get_or_create(
        referrer=referrer,
        referred=referred
    )
    
    if created:
        print(f"✓ Created referral: {referrer.username} → {referred.username}")
    else:
        print(f"✓ Referral exists: {referrer.username} → {referred.username}")
    
    # Create deposit
    deposit, created = Deposit.objects.get_or_create(
        user=referred,
        defaults={
            'amount': 1000.00,
            'cryptocurrency': 'BTC',
            'status': 'approved',
            'approved_by': User.objects.filter(is_staff=True).first()
        }
    )
    
    if created:
        print(f"✓ Created deposit: {referred.username} - $1000")
    else:
        print(f"✓ Deposit exists: {referred.username}")
    
    # Create commission
    commission, created = ReferralCommission.objects.get_or_create(
        referral=referral,
        deposit=deposit,
        defaults={
            'amount': 100.00,
            'status': 'pending'
        }
    )
    
    if created:
        print(f"✓ Created commission: ${commission.amount}")
    else:
        print(f"✓ Commission exists: ${commission.amount}")
    
    print(f"\n✓ Test data complete!")
else:
    print("Need 2+ users")
