"""DRF ViewSets for all portfolio models."""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from portfolio.models import (
    Profile, SkillCategory, Skill, ProjectCategory, Project,
    Education, Experience, Achievement, Publication,
    Testimonial, BlogPost, ContactMessage
)
from core.models import SiteSettings
from .serializers import (
    ProfileSerializer, SkillCategorySerializer, SkillSerializer,
    ProjectCategorySerializer, ProjectSerializer,
    EducationSerializer, ExperienceSerializer,
    AchievementSerializer, PublicationSerializer,
    TestimonialSerializer, BlogPostSerializer,
    ContactMessageSerializer, SiteSettingsSerializer
)


class SiteSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer

    def list(self, request, *args, **kwargs):
        instance = SiteSettings.get_instance()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.filter(is_active=True)
    serializer_class = ProfileSerializer


class SkillCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkillCategory.objects.prefetch_related('skills').all()
    serializer_class = SkillCategorySerializer


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.select_related('category').all()
    serializer_class = SkillSerializer


class ProjectCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.select_related('category').all()
    serializer_class = ProjectSerializer
    lookup_field = 'slug'

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured = self.queryset.filter(featured=True)[:6]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)


class EducationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer


class ExperienceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer


class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer


class TestimonialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Testimonial.objects.filter(featured=True)
    serializer_class = TestimonialSerializer


class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BlogPost.objects.filter(status='published')
    serializer_class = BlogPostSerializer
    lookup_field = 'slug'


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    http_method_names = ['post', 'head', 'options']
