"""API URL configuration using DRF DefaultRouter."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'site-settings', views.SiteSettingsViewSet, basename='site-settings')
router.register(r'profile', views.ProfileViewSet, basename='profile')
router.register(r'skill-categories', views.SkillCategoryViewSet, basename='skill-categories')
router.register(r'skills', views.SkillViewSet, basename='skills')
router.register(r'project-categories', views.ProjectCategoryViewSet, basename='project-categories')
router.register(r'projects', views.ProjectViewSet, basename='projects')
router.register(r'education', views.EducationViewSet, basename='education')
router.register(r'experience', views.ExperienceViewSet, basename='experience')
router.register(r'achievements', views.AchievementViewSet, basename='achievements')
router.register(r'publications', views.PublicationViewSet, basename='publications')
router.register(r'testimonials', views.TestimonialViewSet, basename='testimonials')
router.register(r'blog', views.BlogPostViewSet, basename='blog')
router.register(r'contact', views.ContactMessageViewSet, basename='contact')

urlpatterns = [
    path('', include(router.urls)),
]
