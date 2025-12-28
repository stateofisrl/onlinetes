#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("\n=== All Users in Database ===")
for user in User.objects.all():
    print(f"\nUsername: {user.username}")
    print(f"Email: {user.email}")
    print(f"Is Staff: {user.is_staff}")
    print(f"Is Superuser: {user.is_superuser}")
    print(f"Has usable password: {user.has_usable_password()}")

print("\n\n=== Reset Password for a User ===")
email_input = input("Enter email address to reset password (or press Enter to skip): ").strip()

if email_input:
    try:
        user = User.objects.get(email=email_input)
        new_password = input("Enter new password: ").strip()
        user.set_password(new_password)
        user.save()
        print(f"\n✅ Password updated for {user.username}")
        print(f"Email: {user.email}")
        print(f"New Password: {new_password}")
    except User.DoesNotExist:
        print(f"\n❌ No user found with email: {email_input}")
