"""Core models for site-wide functionality."""

from django.db import models
from django.utils import timezone


class SiteSettings(models.Model):
    """Singleton model for site-wide settings."""
    site_title = models.CharField(max_length=200, default="My Portfolio")
    site_description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    hero_title = models.CharField(max_length=200, default="Hello, I'm")
    hero_name = models.CharField(max_length=100, default="[Your Name]")
    hero_roles = models.JSONField(default=list, blank=True,
                                  help_text="List of rotating roles, e.g. ['Developer', 'Researcher']")
    hero_subtitle = models.CharField(max_length=300, default="Building the future, one line of code at a time.")
    meta_keywords = models.TextField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    enable_music = models.BooleanField(default=False)
    music_file = models.FileField(upload_to='music/', blank=True, null=True)
    visitor_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_title

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def increment_visitor_count(self):
        self.visitor_count += 1
        self.save(update_fields=['visitor_count'])
        return self.visitor_count


class VisitorLog(models.Model):
    """Track visitor sessions."""
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    visited_at = models.DateTimeField(default=timezone.now)
    page_views = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-visited_at']

    def __str__(self):
        return f"{self.ip_address} - {self.visited_at}"


class VisitorSession(models.Model):
    """Daily visitor statistics."""
    date = models.DateField(unique=True)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.count} visitors"
