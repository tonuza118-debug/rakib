"""Custom admin for portfolio models with rich management interface."""

from django.contrib import admin
from .models import (
    Profile, SkillCategory, Skill, ProjectCategory, Project, ProjectImage,
    Education, Experience, Achievement, Publication,
    Testimonial, BlogPost, ContactMessage
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'title', 'email', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['full_name', 'title', 'bio']
    fieldsets = (
        ('Personal Info', {
            'fields': ('full_name', 'title', 'bio', 'avatar', 'resume')
        }),
        ('Contact', {
            'fields': ('location', 'email', 'phone', 'birth_date')
        }),
        ('Details', {
            'fields': ('interests', 'research_areas', 'personal_story', 'fun_facts')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1
    fields = ['name', 'proficiency', 'icon', 'is_featured', 'order']


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'order']
    list_editable = ['color', 'order']
    inlines = [SkillInline]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'proficiency', 'is_featured', 'order']
    list_filter = ['category', 'proficiency', 'is_featured']
    list_editable = ['proficiency', 'is_featured', 'order']
    search_fields = ['name']


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color']
    prepopulated_fields = {'slug': ('name',)}


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption', 'order']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'featured', 'order', 'created_at']
    list_filter = ['category', 'status', 'featured']
    list_editable = ['featured', 'order']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectImageInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'description', 'short_description', 'category')
        }),
        ('Media', {
            'fields': ('image', 'video_url')
        }),
        ('Links', {
            'fields': ('github_url', 'live_url', 'documentation_url')
        }),
        ('Details', {
            'fields': ('technologies', 'status', 'start_date', 'end_date')
        }),
        ('Display', {
            'fields': ('featured', 'order')
        }),
    )


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']
    search_fields = ['institution', 'degree', 'field_of_study']
    list_editable = ['is_current']


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['position', 'company', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']
    search_fields = ['position', 'company']
    list_editable = ['is_current']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['title', 'achievement_type', 'organization', 'date', 'featured']
    list_filter = ['achievement_type', 'featured']
    list_editable = ['featured']
    search_fields = ['title', 'organization']


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ['title', 'publication_type', 'journal', 'date', 'citations']
    list_filter = ['publication_type']
    search_fields = ['title', 'authors', 'journal']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'company', 'rating', 'featured']
    list_filter = ['rating', 'featured']
    list_editable = ['featured']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'published_at', 'created_at']
    list_filter = ['status']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'is_archived', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_at']
    date_hierarchy = 'created_at'

    actions = ['mark_as_read', 'mark_as_archived']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected as read"

    def mark_as_archived(self, request, queryset):
        queryset.update(is_archived=True)
    mark_as_archived.short_description = "Mark selected as archived"


