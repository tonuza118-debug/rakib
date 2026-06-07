"""Custom admin for core models."""

from django.contrib import admin
from .models import SiteSettings, VisitorLog


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_title', 'hero_name', 'email', 'visitor_count', 'updated_at']
    fieldsets = (
        ('General', {
            'fields': ('site_title', 'site_description', 'logo', 'favicon', 'meta_keywords')
        }),
        ('Hero Section', {
            'fields': ('hero_title', 'hero_name', 'hero_roles', 'hero_subtitle')
        }),
        ('Social Links', {
            'fields': ('github_url', 'linkedin_url', 'twitter_url', 'email')
        }),
        ('Music', {
            'fields': ('enable_music', 'music_file'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('visitor_count',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'session_key', 'page_views', 'visited_at']
    list_filter = ['visited_at']
    search_fields = ['ip_address', 'user_agent']
    readonly_fields = ['session_key', 'ip_address', 'user_agent', 'visited_at', 'page_views']
    date_hierarchy = 'visited_at'
