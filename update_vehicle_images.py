import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from main.models import Vehicle

print("\n=== UPDATING VEHICLE IMAGES ===\n")

# Update with proper direct image URLs from Unsplash
updates = [
    {
        'id': 1,
        'name': 'Model S',
        'image': 'https://images.unsplash.com/photo-1617469767537-b85d00004b58?w=800&h=600&fit=crop&auto=format'
    },
    {
        'id': 2,
        'name': 'Model 3',
        'image': 'https://images.unsplash.com/photo-1552820728-8ac41f1ce891?w=800&h=600&fit=crop&auto=format'
    },
    {
        'id': 3,
        'name': 'Model X',
        'image': 'https://images.unsplash.com/photo-1606664515524-2682dc4c4b02?w=800&h=600&fit=crop&auto=format'
    },
]

for data in updates:
    try:
        vehicle = Vehicle.objects.get(id=data['id'])
        vehicle.image = data['image']
        vehicle.save()
        print(f"✓ Updated {data['name']} with image: {data['image'][:60]}...")
    except Vehicle.DoesNotExist:
        print(f"✗ Vehicle {data['id']} ({data['name']}) not found")

print("\n=== VERIFICATION ===\n")
for v in Vehicle.objects.all():
    print(f"{v.name}: {v.image[:80]}..." if len(v.image) > 80 else f"{v.name}: {v.image}")

print("\n✓ All vehicle images updated!")
