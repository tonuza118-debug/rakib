"""Portfolio views - all data passed to the single-page 3D portfolio template."""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
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


def version_check(request):
    """Quick endpoint to verify which code version is running. Remove after testing."""
    import inspect
    from core.storage import custom_cloudinary
    import io, struct, zlib, time

    src = inspect.getsource(custom_cloudinary.CustomMediaCloudinaryStorage._upload)
    has_use_filename = 'use_filename' in src
    # Check the docstring to verify which version is loaded
    doc = custom_cloudinary.CustomMediaCloudinaryStorage._upload.__doc__ or ''

    # Actually test an upload
    test_result = 'not tested'
    test_url = None
    test_stored = None
    cloudinary_response = None
    try:
        sig = b'\x89PNG\r\n\x1a\n'
        ihdr_data = struct.pack('>IIBBBBB', 4, 4, 8, 2, 0, 0, 0)
        ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
        ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
        raw = b'\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00' * 4
        compressed = zlib.compress(raw)
        idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
        idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
        iend_crc = zlib.crc32(b'IEND') & 0xffffffff
        iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
        png_data = sig + ihdr + idat + iend

        buf = io.BytesIO(png_data)
        from django.core.files.uploadedfile import InMemoryUploadedFile
        png = InMemoryUploadedFile(buf, 'image', 'test_verify.png', 'image/png', len(png_data), None)

        # Clean up old test projects
        Project.objects.filter(slug__startswith='cloudinary-verify-').delete()

        project = Project.objects.create(
            title='Cloudinary Verify ' + str(int(time.time())),
            slug='cloudinary-verify-' + str(int(time.time())),
            description='Verification upload',
            short_description='Verify',
            status='completed',
            featured=False,
            order=9999,
            image=png,
        )
        # Also capture what _save returns directly
        from core.storage.custom_cloudinary import CustomMediaCloudinaryStorage
        storage = CustomMediaCloudinaryStorage()
        saved_name = storage.save('projects/test_cloudinary_direct.png', png)
        cloudinary_response = {'saved_name': saved_name}

        project.refresh_from_db()
        test_stored = str(project.image.name) if project.image else None
        test_url = project.image.url if project.image else None

        # Check URL
        import urllib.request
        url_ok = False
        if test_url:
            try:
                req = urllib.request.Request(test_url, method='HEAD')
                resp = urllib.request.urlopen(req, timeout=10)
                url_ok = resp.status == 200
            except Exception as e:
                test_result = str(e)[:100]

        test_result = 'SUCCESS - URL resolves!' if url_ok else 'FAIL - URL does not resolve'
        project.delete()
    except Exception as e:
        test_result = 'ERROR: ' + str(e)[:200]

    return JsonResponse({
        'has_use_filename': has_use_filename,
        'upload_docstring': doc[:100],
        'storage_class': type(custom_cloudinary.CustomMediaCloudinaryStorage).__name__,
        'test_stored_value': test_stored,
        'test_url': test_url,
        'test_result': test_result,
        'cloudinary_response': cloudinary_response,
    })


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
