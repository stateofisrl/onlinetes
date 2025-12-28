#!/usr/bin/env python
"""
Test script to verify deposit approval email is sent only once with balance info.
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from apps.users.models import CustomUser
from apps.deposits.models import Deposit, CryptoWallet
from django.utils import timezone

# Get or create test user
try:
    user = CustomUser.objects.get(email='testuser@example.com')
    print(f"✓ Using existing test user: {user.email}, Current balance: ${user.balance}")
except CustomUser.DoesNotExist:
    user = CustomUser.objects.create_user(
        email='testuser@example.com',
        password='testpass123',
        first_name='Test',
        username='testuser'
    )
    user.balance = Decimal('1000.00')
    user.save()
    print(f"✓ Created test user: {user.email}, Initial balance: ${user.balance}")

# Get or create crypto wallet
crypto_wallet, created = CryptoWallet.objects.get_or_create(
    cryptocurrency='BTC',
    defaults={'wallet_address': '1A1z7agoat5SFpjCMS3gHHYpPieTrjv7Gc', 'is_active': True}
)
print(f"{'✓ Created' if created else '✓ Using'} crypto wallet: {crypto_wallet.cryptocurrency}")

# Create a test deposit that will trigger approval flow
print("\n--- Creating test deposit with APPROVED status ---")
deposit = Deposit.objects.create(
    user=user,
    cryptocurrency='BTC',
    amount=Decimal('0.5'),
    status='pending',  # Start as pending
    proof_type='transaction_id',
    proof_content='txid123456789'
)
print(f"✓ Created deposit #{deposit.pk}: {deposit.cryptocurrency} {deposit.amount}")
print(f"  Status: {deposit.status}")
print(f"  User balance before approval: ${user.balance}")

# Now approve it (this should trigger the signal and send ONE email with balance)
print("\n--- Approving deposit (should send ONE email with balance info) ---")
deposit.status = 'approved'
deposit.approved_at = timezone.now()
deposit.save()

# Refresh user to check balance
user.refresh_from_db()
print(f"✓ Deposit approved")
print(f"  Status: {deposit.status}")
print(f"  User balance after approval: ${user.balance}")
print(f"  Expected balance: ${Decimal('1000.50')}")

if user.balance == Decimal('1000.50'):
    print("\n✅ SUCCESS: Balance updated correctly!")
else:
    print(f"\n❌ ERROR: Balance mismatch. Expected 1000.50, got {user.balance}")

print("\n" + "="*60)
print("Check your email for deposit approval notification.")
print("It should have:")
print("  - Subject: 'Deposit Approved - Tesla Investment Platform'")
print("  - Available Balance: $1000.50")
print("  - Only ONE email should arrive (not two)")
print("="*60)
