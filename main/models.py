from django.db import models
from django.utils import timezone


class Vehicle(models.Model):
    name = models.CharField(max_length=200)
    model = models.CharField(max_length=100, blank=True)
    image = models.CharField(max_length=500, blank=True, help_text='URL or static path to image')
    battery_kwh = models.DecimalField(max_digits=6, decimal_places=2)
    top_speed_mph = models.PositiveIntegerField()
    zero_sixty = models.DecimalField(max_digits=4, decimal_places=2, help_text='0-60 mph sec')
    range_miles = models.PositiveIntegerField()
    charging_time_hours = models.DecimalField(max_digits=4, decimal_places=2)
    charging_options = models.CharField(max_length=300, blank=True)
    autopilot_features = models.TextField(blank=True)
    price_usd = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} {self.model}" if self.model else self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('payment_submitted', 'Payment Proof Submitted'),
        ('payment_approved', 'Payment Approved'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    address = models.TextField(blank=True, help_text='Shipping/delivery address')
    created_at = models.DateTimeField(default=timezone.now)
    
    # Payment fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    crypto_address = models.CharField(max_length=500, blank=True, help_text='Admin sets crypto payment address')
    crypto_currency = models.CharField(max_length=50, blank=True, default='USDT', help_text='e.g., BTC, ETH, USDT')
    payment_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, help_text='Amount in USD')
    payment_proof = models.TextField(blank=True, help_text='Transaction hash or proof from customer')
    payment_proof_image = models.CharField(max_length=500, blank=True, help_text='URL to payment screenshot')
    payment_submitted_at = models.DateTimeField(null=True, blank=True)
    payment_approved_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, help_text='Internal notes for admin')

    def __str__(self):
        return f"Order #{self.id} - {self.vehicle} for {self.name} ({self.status})"


class SupportMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    admin_reply = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    client_id = models.CharField(max_length=64, blank=True, db_index=True)

    def __str__(self):
        return f"Support from {self.name} <{self.email}>"

    def has_reply(self):
        return bool(self.admin_reply)


class Tracking(models.Model):
    tracking_id = models.CharField(max_length=100, unique=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=100, default='Order confirmed')
    last_updated = models.DateTimeField(default=timezone.now)
    from_location = models.CharField(max_length=255, blank=True, help_text='Pickup location (address or coordinates)')
    to_location = models.CharField(max_length=255, blank=True, help_text='Delivery location (address or coordinates)')
    custom_email_message = models.TextField(blank=True, help_text='Optional: Send a custom email to the user when saving.')

    def __str__(self):
        return f"{self.tracking_id} - {self.status}"


class Investment(models.Model):
    TIER_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES)
    capital = models.DecimalField(max_digits=14, decimal_places=2)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Investment #{self.id} - {self.full_name} ({self.tier})"
