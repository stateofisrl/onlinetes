import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print(f"ADMIN_EMAIL: {settings.ADMIN_EMAIL}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'empty'}")

if not settings.ADMIN_EMAIL:
    print("ERROR: ADMIN_EMAIL is empty!")
else:
    try:
        print(f"\nAttempting to send test email to {settings.ADMIN_EMAIL}...")
        sent = send_mail(
            'Test Email',
            'This is a test',
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL]
        )
        print(f"Send result: {sent}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
