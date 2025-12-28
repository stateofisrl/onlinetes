#!/usr/bin/env python
"""
Test script to send deposit and withdrawal email notifications.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from apps.deposits.models import Deposit, CryptoWallet
from apps.withdrawals.models import Withdrawal
from apps.users.models import CustomUser
from apps.users.emails import send_deposit_notification, send_withdrawal_notification
from decimal import Decimal

TEST_EMAIL = 'noobodii6@gmail.com'
TEST_NAME = 'Test User'

print("="*60)
print("TESTING DEPOSIT & WITHDRAWAL EMAIL TEMPLATES")
print("="*60)
print(f"\nSending test emails to: {TEST_EMAIL}\n")

# Get or create test user
user, created = CustomUser.objects.get_or_create(
    email=TEST_EMAIL,
    defaults={
        'username': 'testuser',
        'first_name': TEST_NAME,
        'balance': Decimal('1000.00')
    }
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"✓ Created test user: {user.email}")
else:
    print(f"✓ Using existing user: {user.email}")

# Test 1: Deposit Approved
print("\n1️⃣  Testing DEPOSIT APPROVED email...")
print("-"*60)
deposit_approved = Deposit.objects.create(
    user=user,
    amount=Decimal('500.00'),
    cryptocurrency='USDT',
    status='approved',
    proof_type='transaction_id',
    proof_content='TEST-TXN-12345'
)
send_deposit_notification(deposit_approved)
print(f"✓ Deposit approved email sent to {TEST_EMAIL}")

# Test 2: Deposit Rejected
print("\n2️⃣  Testing DEPOSIT REJECTED email...")
print("-"*60)
deposit_rejected = Deposit.objects.create(
    user=user,
    amount=Decimal('300.00'),
    cryptocurrency='BTC',
    status='rejected',
    proof_type='screenshot',
    proof_content='https://example.com/screenshot.png'
)
send_deposit_notification(deposit_rejected)
print(f"✓ Deposit rejected email sent to {TEST_EMAIL}")

# Test 3: Withdrawal Completed
print("\n3️⃣  Testing WITHDRAWAL COMPLETED email...")
print("-"*60)
withdrawal_completed = Withdrawal.objects.create(
    user=user,
    amount=Decimal('200.00'),
    cryptocurrency='USDT',
    wallet_address='0x1234567890abcdef',
    status='completed'
)
send_withdrawal_notification(withdrawal_completed)
print(f"✓ Withdrawal completed email sent to {TEST_EMAIL}")

# Test 4: Withdrawal Rejected
print("\n4️⃣  Testing WITHDRAWAL REJECTED email...")
print("-"*60)
withdrawal_rejected = Withdrawal.objects.create(
    user=user,
    amount=Decimal('150.00'),
    cryptocurrency='BTC',
    wallet_address='bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
    status='rejected'
)
send_withdrawal_notification(withdrawal_rejected)
print(f"✓ Withdrawal rejected email sent to {TEST_EMAIL}")

print("\n" + "="*60)
print("✅ ALL DEPOSIT & WITHDRAWAL EMAILS SENT SUCCESSFULLY!")
print("="*60)
print(f"\nCheck {TEST_EMAIL} for:")
print("  1. Deposit Approved")
print("  2. Deposit Rejected")
print("  3. Withdrawal Completed")
print("  4. Withdrawal Rejected")
print("="*60)
