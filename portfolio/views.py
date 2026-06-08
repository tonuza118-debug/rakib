"""Portfolio views - all data passed to the single-page 3D portfolio template."""

import os
import io
import struct
import zlib
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import (
    Profile, SkillCategory, Skill, ProjectCategory, Project,
    Education, Experience, Achievement, Publication,
    Testimonial, BlogPost, ContactMessage
)


@ensure_csrf_cookie
def portfolio_home(request):
    """Main portfolio page - single page application with all sections."""
    profile = Profile.objects.filter(is_active=True).first()
    skills_by_category = []
    for category in SkillCategory.objects.prefetch_related('skills').all():
        skills_by_category.append({
            'category': category,
            'skills': category.skills.all()
        })
    projects = Project.objects.select_related('category').all()
    project_categories = ProjectCategory.objects.all()
    education = Education.objects.all()
    experience = Experience.objects.all()
    achievements = Achievement.objects.all()
    publications = Publication.objects.all()
    testimonials = Testimonial.objects.filter(featured=True)
    blog_posts = BlogPost.objects.filter(status='published')[:6]

    context = {
        'profile': profile,
        'skills_by_category': skills_by_category,
        'projects': projects,
        'project_categories': project_categories,
        'education': education,
        'experience': experience,
        'achievements': achievements,
        'publications': publications,
        'testimonials': testimonials,
        'blog_posts': blog_posts,
    }
    return render(request, 'portfolio/home.html', context)


def project_detail(request, slug):
    """Individual project detail page."""
    project = get_object_or_404(Project, slug=slug)
    related_projects = Project.objects.filter(
        category=project.category
    ).exclude(id=project.id)[:3]
    profile = Profile.objects.filter(is_active=True).first()
    return render(request, 'portfolio/project_detail.html', {
        'project': project,
        'related_projects': related_projects,
        'profile': profile,
    })


def blog_list(request):
    """Blog listing page."""
    posts = BlogPost.objects.filter(status='published')
    return render(request, 'portfolio/blog_list.html', {'posts': posts})


def blog_detail(request, slug):
    """Individual blog post."""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    return render(request, 'portfolio/blog_detail.html', {'post': post})


@require_POST
def contact_submit(request):
    """Handle contact form submission."""
    try:
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not all([name, email, message]):
            return JsonResponse({
                'success': False,
                'error': 'Please fill in all required fields.'
            }, status=400)

        ContactMessage.objects.create(
            name=name, email=email, subject=subject, message=message
        )
        return JsonResponse({
            'success': True,
            'message': 'Message sent successfully! I\'ll get back to you soon.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'An error occurred. Please try again.'
        }, status=500)


def _make_test_png():
    """Create a minimal 2x2 red PNG in memory."""
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', 2, 2, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    raw = b'\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00'
    compressed = zlib.compress(raw)
    idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
    idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
    iend_crc = zlib.crc32(b'IEND') & 0xffffffff
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    data = sig + ihdr + idat + iend
    buf = io.BytesIO(data)
    return InMemoryUploadedFile(buf, 'image', 'test_upload.png', 'image/png', len(data), None)


@require_GET
def test_cloudinary_upload(request):
    """Temporary endpoint to test Cloudinary image upload. Remove after testing."""
    secret = request.GET.get('key', '')
    if secret != 'test-upload-2026':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        # Clean up any previous test projects
        Project.objects.filter(slug__startswith='cloudinary-upload-test').delete()

        # Create a test project with an image
        png = _make_test_png()
        import time
        ts = int(time.time())

        project = Project.objects.create(
            title='Cloudinary Upload Test ' + str(ts),
            slug='cloudinary-upload-test-' + str(ts),
            description='Testing Cloudinary upload from the deployed site',
            short_description='Test',
            status='completed',
            featured=False,
            order=999,
            image=png,
        )

        # Get the stored value
        project.refresh_from_db()
        stored_value = str(project.image.name) if project.image else None
        image_url = project.image.url if project.image else None

        # Verify the URL resolves
        import urllib.request
        url_works = False
        url_status = 'N/A'
        if image_url:
            try:
                req = urllib.request.Request(image_url, method='HEAD')
                resp = urllib.request.urlopen(req, timeout=10)
                url_status = resp.status
                url_works = resp.status == 200
            except Exception as e:
                url_status = str(e)

        # Also report which storage backend is active
        from django.conf import settings as django_settings
        from django.core.files.storage import default_storage

        result = {
            'status': 'success',
            'project_id': project.id,
            'stored_value': stored_value,
            'image_url': image_url,
            'url_resolves': url_works,
            'url_status': url_status,
            'storage_backend': str(django_settings.DEFAULT_FILE_STORAGE),
            'storage_class': type(default_storage).__name__,
            'message': 'Image uploaded and URL resolves!' if url_works else 'Image uploaded but URL does NOT resolve',
        }

        # Clean up - delete the test project
        if not request.GET.get('keep'):
            project.delete()
            result['cleaned_up'] = True
        else:
            result['cleaned_up'] = False

        return JsonResponse(result, json_dumps_params={'indent': 2})

    except Exception as e:
        import traceback
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc(),
        }, status=500)
