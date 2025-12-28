import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from main.views import vehicles_list
from main.models import Vehicle

# Check database
print("=== DATABASE CHECK ===\n")
vehicles = Vehicle.objects.all()
print(f"Total vehicles: {vehicles.count()}\n")

for v in vehicles:
    print(f"{v.name}:")
    print(f"  Image: {v.image}")
    print(f"  Has image: {bool(v.image)}")

# Test the view directly
print("\n=== TESTING VIEW ===\n")

factory = RequestFactory()
request = factory.get('/vehicles/')
response = vehicles_list(request)

print(f"Response status: {response.status_code}")
print(f"Response content length: {len(response.content)}")

# Get the HTML
if hasattr(response, 'rendered_content'):
    html = response.rendered_content.decode('utf-8')
else:
    html = response.content.decode('utf-8')

# Check for images in HTML
import re
img_count = len(re.findall(r'<img', html))
print(f"Image tags in HTML: {img_count}")

# Show first 1500 chars of the vehicles section
vehicles_section = re.search(r'<div class="grid md:grid-cols-2.*?</section>', html, re.DOTALL)
if vehicles_section:
    content = vehicles_section.group(0)[:2000]
    print(f"\nVehicles section preview:\n{content}...")
    
    # Check for actual image URLs
    img_srcs = re.findall(r'src="([^"]+)"', content)
    print(f"\nImage sources found:")
    for i, src in enumerate(img_srcs, 1):
        print(f"  {i}. {src[:70]}...")
