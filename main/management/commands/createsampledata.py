from django.core.management.base import BaseCommand
from django.utils import timezone

from main.models import Vehicle, Order, Tracking


class Command(BaseCommand):
    help = 'Create sample vehicles, orders, and tracking entries for demo'

    def handle(self, *args, **options):
        if Vehicle.objects.exists():
            self.stdout.write(self.style.WARNING('Vehicles already exist — skipping sample creation.'))
            return

        now = timezone.now()
        vehicles = [
            {
                'name': 'Model S', 'model': 'Plaid', 'battery_kwh': 100, 'top_speed_mph': 200,
                'zero_sixty': 1.99, 'range_miles': 396, 'charging_time_hours': 1.0,
                'charging_options': 'Home, Supercharger', 'autopilot_features': 'Full Self-Driving (optional)',
                'price_usd': 129990, 'description': 'Top-tier performance sedan with industry-leading acceleration.'
            },
            {
                'name': 'Model 3', 'model': 'Long Range', 'battery_kwh': 82, 'top_speed_mph': 145,
                'zero_sixty': 4.2, 'range_miles': 350, 'charging_time_hours': 0.8,
                'charging_options': 'Home, Supercharger', 'autopilot_features': 'Autopilot standard',
                'price_usd': 48990, 'description': 'Efficient, safe, and affordable electric sedan.'
            },
            {
                'name': 'Model X', 'model': 'Plaid', 'battery_kwh': 100, 'top_speed_mph': 163,
                'zero_sixty': 2.5, 'range_miles': 333, 'charging_time_hours': 1.2,
                'charging_options': 'Home, Supercharger', 'autopilot_features': 'Full Self-Driving (optional)',
                'price_usd': 119990, 'description': 'Spacious SUV with falcon wing doors and high performance.'
            }
        ]

        created = []
        for v in vehicles:
            obj = Vehicle.objects.create(**v)
            created.append(obj)
            self.stdout.write(self.style.SUCCESS(f'Created vehicle: {obj}'))

        # Create a sample order and tracking for the first vehicle
        first = created[0]
        order = Order.objects.create(vehicle=first, name='Sample Customer', email='customer@example.com', phone='+1234567890')
        tracking = Tracking.objects.create(tracking_id='TSDMOCK12345', order=order, vehicle=first, customer_name=order.name, status='Vehicle preparation', last_updated=now)
        self.stdout.write(self.style.SUCCESS(f'Created sample order #{order.id} and tracking {tracking.tracking_id}'))
