#!/usr/bin/env python
"""Simple test to verify all views work without errors"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tesla_site.settings')
django.setup()

from django.test import Client
from django.urls import reverse

client = Client()

# Test homepage
print("Testing homepage...")
response = client.get('/')
assert response.status_code == 200, f"Homepage failed: {response.status_code}"
print("✓ Homepage OK")

# Test vehicles
print("Testing vehicles list...")
response = client.get('/vehicles/')
assert response.status_code == 200, f"Vehicles failed: {response.status_code}"
print("✓ Vehicles OK")

# Test support
print("Testing support...")
response = client.get('/support/')
assert response.status_code == 200, f"Support failed: {response.status_code}"
print("✓ Support OK")

# Test track
print("Testing track...")
response = client.get('/track/')
assert response.status_code == 200, f"Track failed: {response.status_code}"
print("✓ Track OK")

# Test invest
print("Testing invest...")
response = client.get('/invest/')
assert response.status_code == 200, f"Invest failed: {response.status_code}"
print("✓ Invest OK")

# Test buy with first vehicle
print("Testing buy form...")
from main.models import Vehicle
vehicles = Vehicle.objects.all()
if vehicles.exists():
    v = vehicles.first()
    response = client.get(f'/buy/{v.id}/')
    assert response.status_code == 200, f"Buy page failed: {response.status_code}"
    print(f"✓ Buy form OK (vehicle: {v})")
else:
    print("⚠ No vehicles in database")

print("\n✅ All pages working correctly!")
