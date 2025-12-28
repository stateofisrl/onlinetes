from PIL import Image, ImageDraw, ImageFont
import os

# Create img directory if it doesn't exist
img_dir = os.path.dirname(__file__)

# Create placeholder images
vehicles = [
    ('model_s.jpg', 'Tesla Model S', '#000000'),
    ('model_3.jpg', 'Tesla Model 3', '#1a1a1a'),
    ('model_x.jpg', 'Tesla Model X', '#2d2d2d'),
]

for filename, text, bg_color in vehicles:
    # Create image
    img = Image.new('RGB', (800, 600), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Add text
    try:
        # Try to use a larger font if available
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    # Get text bbox to center it
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (800 - text_width) / 2
    y = (600 - text_height) / 2
    
    draw.text((x, y), text, fill='white', font=font)
    
    # Save image
    img.save(os.path.join(img_dir, filename))
    print(f'✓ Created {filename}')

print('\nPlaceholder images created successfully!')
