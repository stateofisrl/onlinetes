#!/usr/bin/env python
"""Add Tesla Cybertruck to vehicles"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from main.models import Vehicle

# Create Cybertruck
cybertruck = Vehicle.objects.create(
    name='Cybertruck',
    model='',
    image='/static/img/cybertruck.jpg',
    battery_kwh=200.00,
    top_speed_mph=130,
    zero_sixty=2.90,
    range_miles=470,
    charging_time_hours=12.00,
    charging_options='Supercharger (40 min 0-80%), Wall Charger (12 hours)',
    autopilot_features='Full Self-Driving Capability with advanced AI navigation',
    price_usd=60990.00,
    description='Exoskeleton design with ultra-hard stainless steel. 0-60 in 2.9 seconds. Towing capacity up to 14,000 lbs. Unique angular design combined with cutting-edge technology.'
)

print(f"✓ Created Cybertruck:")
print(f"  Name: {cybertruck.name}")
print(f"  Price: ${cybertruck.price_usd:,.2f}")
print(f"  0-60: {cybertruck.zero_sixty}s")
print(f"  Range: {cybertruck.range_miles} miles")
print(f"  Battery: {cybertruck.battery_kwh} kWh")
