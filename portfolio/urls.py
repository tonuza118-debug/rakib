"""Portfolio URL configuration."""

from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.portfolio_home, name='home'),
    path('project/<slug:slug>/', views.project_detail, name='project_detail'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('contact/', views.contact_submit, name='contact_submit'),
    # TEMPORARY: Test endpoint for Cloudinary upload - remove after testing
    path('test-upload/', views.test_cloudinary_upload, name='test_cloudinary_upload'),
]
