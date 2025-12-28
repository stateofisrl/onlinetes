"""
Signals for main app - handle tracking status updates
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from .models import Tracking


@receiver(pre_save, sender=Tracking)
def capture_old_status(sender, instance, **kwargs):
    """Capture the old status before saving"""
    if instance.pk:
        try:
            old_instance = Tracking.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Tracking.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Tracking)
def send_tracking_status_email(sender, instance, created, **kwargs):
    """Send email when tracking status is updated"""
    # Skip if no order or no email
    if not instance.order or not instance.order.email:
        return
    
    # Skip if status hasn't changed (unless it's a new tracking)
    old_status = getattr(instance, '_old_status', None)
    if not created and old_status == instance.status:
        return
    
    # Determine email subject and message based on status
    status_lower = instance.status.lower()
    
    # Map statuses to user-friendly messages
    if 'shipped' in status_lower or 'transit' in status_lower or 'in transit' in status_lower:
        status_emoji = '🚚'
        status_color = '#3b82f6'
        status_message = 'Your order is on its way!'
        detail_message = 'Your vehicle has been shipped and is currently in transit.'
    elif 'delivered' in status_lower or 'complete' in status_lower:
        status_emoji = '✅'
        status_color = '#4ade80'
        status_message = 'Your order has been delivered!'
        detail_message = 'Your vehicle has been successfully delivered. Thank you for your purchase!'
    elif 'processing' in status_lower or 'preparing' in status_lower:
        status_emoji = '📦'
        status_color = '#fbbf24'
        status_message = 'Your order is being prepared'
        detail_message = 'We are preparing your order for shipment.'
    else:
        # Generic update for other statuses
        status_emoji = '🔔'
        status_color = '#6366f1'
        status_message = 'Order Status Update'
        detail_message = f'Your order status has been updated to: {instance.status}'
    
    subject = f'{status_emoji} Order Status Update - {instance.tracking_id}'
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #000; color: #fff; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #1a1a1a; border: 1px solid #333; padding: 30px; border-radius: 8px;">
            <h2 style="color: #fff; margin-bottom: 20px;">{status_emoji} {status_message}</h2>
            <p style="color: #ccc; line-height: 1.6;">Hi {instance.customer_name or instance.order.name},</p>
            <p style="color: #ccc; line-height: 1.6;">
                {detail_message}
            </p>
            <div style="background-color: #222; padding: 20px; border-radius: 6px; margin: 20px 0;">
                <p style="color: #999; margin: 5px 0;">Tracking ID: <strong style="color: #4ade80;">{instance.tracking_id}</strong></p>
                <p style="color: #999; margin: 5px 0;">Vehicle: <strong style="color: #fff;">{instance.vehicle.name if instance.vehicle else 'N/A'}</strong></p>
                <p style="color: #999; margin: 5px 0;">Status: <strong style="color: {status_color};">{instance.status}</strong></p>
                <p style="color: #999; margin: 5px 0;">Last Updated: <strong style="color: #fff;">{instance.last_updated.strftime('%B %d, %Y at %I:%M %p')}</strong></p>
                {f'<p style="color: #999; margin: 5px 0;">From: <strong style="color: #fff;">{instance.from_location}</strong></p>' if instance.from_location else ''}
                {f'<p style="color: #999; margin: 5px 0;">To: <strong style="color: #fff;">{instance.to_location}</strong></p>' if instance.to_location else ''}
            </div>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{settings.SITE_URL}/track/?tracking_id={instance.tracking_id}" style="background-color: #fff; color: #000; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                    Track Your Order
                </a>
            </div>
            <p style="color: #ccc; font-size: 14px; margin-top: 20px;">If you have any questions, please contact our support team.</p>
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #333;">
                <p style="color: #666; font-size: 12px; margin: 0;">Best regards,</p>
                <p style="color: #666; font-size: 12px; margin: 0;">Tesla Investment Platform Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.order.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"[TRACKING] Email sent to {instance.order.email} for status: {instance.status}")
    except Exception as e:
        print(f"[TRACKING ERROR] Failed to send email: {e}")
