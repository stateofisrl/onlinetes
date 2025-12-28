import urllib.request
import re

url = 'http://127.0.0.1:8000/vehicles/'

try:
    response = urllib.request.urlopen(url)
    html = response.read().decode('utf-8')
    
    print("=== CHECKING RENDERED HTML ===\n")
    
    # Find all img tags
    img_tags = re.findall(r'<img[^>]+>', html)
    print(f"Total <img> tags found: {len(img_tags)}\n")
    
    if img_tags:
        print("All image tags:")
        for i, tag in enumerate(img_tags, 1):
            # Extract src attribute
            src_match = re.search(r'src="([^"]+)"', tag)
            if src_match:
                src = src_match.group(1)
                print(f"\n{i}. src: {src[:100]}...")
                if 'unsplash' in src:
                    print(f"   ✓ Valid image URL")
                else:
                    print(f"   ? Unexpected URL")
    else:
        print("✗ NO IMAGE TAGS FOUND!")
        
    # Look for the vehicle section
    print("\n=== CHECKING FOR VEHICLE SECTIONS ===\n")
    vehicle_names = ['Model S', 'Model 3', 'Model X']
    for name in vehicle_names:
        if name in html:
            print(f"✓ Found '{name}' in HTML")
        else:
            print(f"✗ '{name}' NOT found in HTML")
            
except Exception as e:
    print(f"Error: {e}")
