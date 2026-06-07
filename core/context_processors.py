"""Context processors for global template variables."""

from .models import SiteSettings


def site_settings(request):
    """Make site settings available to all templates."""
    return {
        'site': SiteSettings.get_instance(),
    }
