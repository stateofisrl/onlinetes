import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from main.models import Vehicle

print("\n=== VEHICLE IMAGES IN DATABASE ===\n")
vehicles = Vehicle.objects.all()

if not vehicles.exists():
    print("No vehicles found in database")
else:
    for v in vehicles:
        print(f"ID: {v.id}")
        print(f"Name: {v.name}")
        print(f"Image: '{v.image}'")
        print(f"Image is empty: {not v.image}")
        print("-" * 50)

print(f"\nTotal vehicles: {vehicles.count()}")
