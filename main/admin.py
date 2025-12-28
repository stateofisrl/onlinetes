from django.contrib import admin
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Vehicle, Order, SupportMessage, Tracking, Investment


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'battery_kwh', 'range_miles', 'price_usd')
    search_fields = ('name', 'model')
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'model', 'price_usd')
        }),
        ('Image', {
            'fields': ('image',),
            'description': 'Enter a full image URL (e.g., https://images.unsplash.com/...)'
        }),
        ('Specifications', {
            'fields': ('battery_kwh', 'top_speed_mph', 'zero_sixty', 'range_miles', 
                      'charging_time_hours', 'charging_options', 'autopilot_features')
        }),
        ('Description', {
            'fields': ('description',)
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'name', 'email', 'phone', 'status', 'created_at')
    search_fields = ('name', 'email', 'vehicle__name')
    list_filter = ('status', 'created_at')
    fields = (
        'vehicle', 'name', 'email', 'phone', 'address', 'created_at', 
        'status', 'crypto_currency', 'crypto_address', 'payment_amount',
        'payment_proof', 'payment_proof_image', 'payment_submitted_at', 'payment_approved_at',
        'admin_notes'
    )
    readonly_fields = ('created_at', 'payment_submitted_at', 'payment_approved_at')
    
    def save_model(self, request, obj, form, change):
        # Check if admin just set crypto payment details for pending order
        if change and 'crypto_address' in form.changed_data and obj.status == 'pending' and obj.crypto_address:
            # Send payment details email to customer
            if obj.email:
                vehicle_name = obj.vehicle.name if obj.vehicle else "Vehicle"
                amount = obj.payment_amount if obj.payment_amount else (obj.vehicle.price_usd if obj.vehicle else 0)
                subject = f'Payment Details for Order #{obj.id} - Tesla Investment Platform'
                
                html_message = f"""
                <html>
                <body style="font-family: Arial, sans-serif; background-color: #000; color: #fff; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #1a1a1a; border: 1px solid #333; padding: 30px; border-radius: 8px;">
                        <h2 style="color: #fff; margin-bottom: 20px;">Payment Details Ready</h2>
                        <p style="color: #ccc; line-height: 1.6;">Hi {obj.name},</p>
                        <p style="color: #ccc; line-height: 1.6;">
                            Thank you for ordering <strong style="color: #fff;">{vehicle_name}</strong>!
                        </p>
                        <p style="color: #ccc; line-height: 1.6;">
                            Please send payment to complete your order:
                        </p>
                        <div style="background-color: #222; padding: 20px; border-radius: 6px; margin: 20px 0;">
                            <p style="color: #999; margin: 5px 0;">Order ID: <strong style="color: #fff;">#{obj.id}</strong></p>
                            <p style="color: #999; margin: 5px 0;">Amount: <strong style="color: #4ade80;">${amount} USD</strong></p>
                            <p style="color: #999; margin: 5px 0;">Currency: <strong style="color: #fff;">{obj.crypto_currency or 'USDT'}</strong></p>
                            <p style="color: #999; margin: 10px 0 5px 0;">Payment Address:</p>
                            <code style="background-color: #000; color: #4ade80; padding: 10px; display: block; border-radius: 4px; word-break: break-all; font-size: 14px;">{obj.crypto_address}</code>
                        </div>
                        <div style="background-color: #1a1a1a; border: 1px solid #333; padding: 15px; border-radius: 6px; margin: 20px 0;">
                            <p style="color: #999; margin: 5px 0; font-size: 14px;">Delivery Address:</p>
                            <p style="color: #fff; margin: 5px 0;">{obj.address or 'Not provided'}</p>
                        </div>
                        <p style="color: #4ade80; line-height: 1.6; margin-top: 20px;">✓ After making payment, submit your transaction proof:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{settings.SITE_URL}/order/{obj.id}/payment/" style="background-color: #fff; color: #000; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                                Submit Payment Proof
                            </a>
                        </div>
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #333;">
                            <p style="color: #666; font-size: 12px; margin: 0;">Best regards,</p>
                            <p style="color: #666; font-size: 12px; margin: 0;">Tesla Investment Platform Team</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                from django.utils.html import strip_tags
                plain_message = strip_tags(html_message)
                send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [obj.email], html_message=html_message, fail_silently=True)
        
        # Check if admin approved payment
        if change and 'status' in form.changed_data and obj.status == 'payment_approved':
            if not obj.payment_approved_at:
                obj.payment_approved_at = timezone.now()
            # Create or update tracking for this order
            import random
            tracking, created = Tracking.objects.get_or_create(
                order=obj,
                defaults={
                    'tracking_id': f'TRK{random.randint(100000, 999999)}',
                    'vehicle': obj.vehicle,
                    'customer_name': obj.name,
                    'status': 'Order confirmed',
                    'to_location': obj.address or 'To be confirmed',
                }
            )
            # Send tracking email
            if obj.email:
                subject = f'Payment Approved - Tesla Investment Platform'
                
                html_message = f"""
                <html>
                <body style="font-family: Arial, sans-serif; background-color: #000; color: #fff; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #1a1a1a; border: 1px solid #333; padding: 30px; border-radius: 8px;">
                        <h2 style="color: #fff; margin-bottom: 20px;">Payment Approved! 🎉</h2>
                        <p style="color: #ccc; line-height: 1.6;">Hi {obj.name},</p>
                        <p style="color: #ccc; line-height: 1.6;">
                            Great news! Your payment has been <strong style="color: #4ade80;">approved</strong> and your order is now being processed.
                        </p>
                        <div style="background-color: #222; padding: 20px; border-radius: 6px; margin: 20px 0;">
                            <p style="color: #999; margin: 5px 0;">Tracking ID: <strong style="color: #4ade80;">{tracking.tracking_id}</strong></p>
                            <p style="color: #999; margin: 5px 0;">Vehicle: <strong style="color: #fff;">{obj.vehicle.name if obj.vehicle else 'N/A'}</strong></p>
                            <p style="color: #999; margin: 5px 0;">Status: <strong style="color: #4ade80;">{tracking.status}</strong></p>
                            <p style="color: #999; margin: 5px 0;">Delivery Address: <strong style="color: #fff;">{obj.address or 'To be confirmed'}</strong></p>
                        </div>
                        <p style="color: #4ade80; line-height: 1.6;">✓ You can track your order anytime using the link below:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{settings.SITE_URL}/track/?tracking_id={tracking.tracking_id}" style="background-color: #fff; color: #000; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                                Track Your Order
                            </a>
                        </div>
                        <p style="color: #ccc; font-size: 14px; margin-top: 20px;">We'll keep you updated on your order status. If you have any questions, please contact our support team.</p>
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #333;">
                            <p style="color: #666; font-size: 12px; margin: 0;">Best regards,</p>
                            <p style="color: #666; font-size: 12px; margin: 0;">Tesla Investment Platform Team</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                from django.utils.html import strip_tags
                plain_message = strip_tags(html_message)
                send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [obj.email], html_message=html_message, fail_silently=True)
        
        super().save_model(request, obj, form, change)


@admin.register(SupportMessage)
class SupportAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'client_id', 'created_at', 'replied_at')
    search_fields = ('name', 'email', 'message', 'admin_reply', 'client_id')
    readonly_fields = ('created_at', 'client_id')
    fields = ('name', 'email', 'message', 'created_at', 'client_id', 'admin_reply', 'replied_at')
    list_filter = ('replied_at', 'created_at')

    def save_model(self, request, obj, form, change):
        # If admin has entered a reply and replied_at not set, set replied_at now
        is_new_reply = obj.admin_reply and not obj.replied_at
        if is_new_reply:
            obj.replied_at = timezone.now()
            super().save_model(request, obj, form, change)
            # Send email notification to user if they have an email
            if obj.email:
                subject = f'Support Reply - Ticket #{obj.id}'
                body = f"Hello {obj.name},\n\nWe have replied to your support message:\n\n{obj.admin_reply}\n\nBest regards,\nSupport Team"
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [obj.email])
        else:
            super().save_model(request, obj, form, change)


@admin.register(Tracking)
class TrackingAdmin(admin.ModelAdmin):
    list_display = ('tracking_id', 'status', 'vehicle', 'customer_name', 'last_updated')
    search_fields = ('tracking_id', 'customer_name', 'status')
    list_filter = ('status',)
    fields = ('tracking_id', 'order', 'vehicle', 'customer_name', 'status', 'last_updated', 'from_location', 'to_location', 'custom_email_message')

    def save_model(self, request, obj, form, change):
        # If admin entered a custom email message, send it to the user
        if obj.custom_email_message and obj.order and obj.order.email:
            subject = f'Tracking Update: {obj.tracking_id}'
            body = obj.custom_email_message
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [obj.order.email])
            # Optionally clear the message after sending
            obj.custom_email_message = ''
        super().save_model(request, obj, form, change)


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'tier', 'capital', 'created_at')
    search_fields = ('full_name', 'email')
    list_filter = ('tier',)
    fields = ('full_name', 'email', 'phone', 'tier', 'capital', 'message', 'created_at')
    readonly_fields = ('created_at',)
