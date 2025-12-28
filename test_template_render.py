import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from main.models import Vehicle

# Create test client
client = Client()

# Get the vehicles page
response = client.get('/vehicles/')

print("\n=== RESPONSE STATUS ===")
print(f"Status Code: {response.status_code}")

print("\n=== VEHICLES IN DATABASE ===")
vehicles = Vehicle.objects.all()
for v in vehicles:
    print(f"\n{v.name}:")
    print(f"  ID: {v.id}")
    print(f"  Image URL: {v.image}")
    print(f"  Image exists: {bool(v.image)}")

print("\n=== CHECKING TEMPLATE RENDERING ===")
html_content = response.content.decode('utf-8')

# Check if image tags are in the HTML
import re
img_tags = re.findall(r'<img[^>]+>', html_content)
print(f"\nTotal <img> tags found: {len(img_tags)}")

if img_tags:
    print("\nFirst 5 image tags:")
    for i, tag in enumerate(img_tags[:5], 1):
        print(f"{i}. {tag}")

# Check for v.image in the rendered HTML
for v in vehicles:
    if v.image in html_content:
        print(f"\n✓ {v.name} image URL found in HTML")
    else:
        print(f"\n✗ {v.name} image URL NOT found in HTML")
        # Check what's actually rendered
        vehicle_section = re.search(f'<h3[^>]*>{v.name}.*?</div>', html_content, re.DOTALL)
        if vehicle_section:
            section = vehicle_section.group(0)
            img_in_section = re.search(r'<img[^>]+src="([^"]+)"', section)
            if img_in_section:
                print(f"  Instead found: {img_in_section.group(1)}")
