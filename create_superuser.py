#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create superuser
username = 'superadmin'
email = 'superadmin@tesla.com'
password = 'super123'

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f'✅ Superuser "{username}" updated')
except User.DoesNotExist:
    user = User.objects.create_superuser(username=username, email=email, password=password)
    print(f'✅ Superuser "{username}" created')

print(f'\nSuperuser Credentials:')
print(f'Username: {username}')
print(f'Password: {password}')
print(f'Email: {email}')
print(f'\nAccess admin at: http://127.0.0.1:8001/admin/')

# Also ensure the existing admin user is properly set up
try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print(f'\n✅ Also verified "admin" user (password: admin123)')
except User.DoesNotExist:
    admin = User.objects.create_superuser('admin', 'admin@tesla.com', 'admin123')
    print(f'\n✅ Also created "admin" user (password: admin123)')
