#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create or update admin user
try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print('✅ Admin user updated')
except User.DoesNotExist:
    admin = User.objects.create_superuser('admin', 'admin@tesla.com', 'admin123')
    print('✅ Admin user created')

print('Username: admin')
print('Password: admin123')
print('Access at: http://127.0.0.1:8001/admin/')

