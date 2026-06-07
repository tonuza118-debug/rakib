"""Core middleware for visitor tracking."""

from django.utils import timezone
from .models import VisitorLog, VisitorSession


class VisitorCounterMiddleware:
    """Track unique visitors via session."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Skip tracking for admin, static, and media
        path = request.path
        if path.startswith(('/admin/', '/static/', '/media/', '/favicon')):
            return response

        # Ensure session exists
        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        # Get or create visitor log
        visitor, created = VisitorLog.objects.get_or_create(
            session_key=session_key,
            defaults={
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
            }
        )

        if not created:
            visitor.page_views += 1
            visitor.visited_at = timezone.now()
            visitor.save(update_fields=['page_views', 'visited_at'])

        # Daily stats
        today = timezone.now().date()
        daily, _ = VisitorSession.objects.get_or_create(date=today)
        if created:
            daily.count += 1
            daily.save(update_fields=['count'])

        return response

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
