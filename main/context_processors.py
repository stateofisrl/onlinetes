from datetime import datetime
from django.conf import settings


def site_settings(request):
    """Expose site-wide settings to templates."""
    return {
        'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
        'now': datetime.utcnow(),
    }
