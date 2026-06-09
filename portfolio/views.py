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
    doc = custom_cloudinary.CustomMediaCloudinaryStorage._upload.__doc__ or ''

    # Test 1: Direct cloudinary upload (bypass Django storage)
    direct_result = 'not tested'
    direct_pid = None
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

        import cloudinary
        result = cloudinary.uploader.upload(
            png_data,
            public_id='test_direct_v3',
            use_filename=False,
            unique_filename=False,
            overwrite=True,
        )
        direct_pid = result['public_id']
        direct_result = 'OK' if direct_pid == 'test_direct_v3' else f'MISMATCH: got {direct_pid}'
        # Cleanup
        cloudinary.uploader.destroy('test_direct_v3')
    except Exception as e:
        direct_result = 'ERROR: ' + str(e)[:200]

    # Test 2: Via Django storage.save()
    storage_result = 'not tested'
    storage_saved = None
    try:
        buf = io.BytesIO(png_data)
        from django.core.files.uploadedfile import InMemoryUploadedFile
        png = InMemoryUploadedFile(buf, 'image', 'test_storage.png', 'image/png', len(png_data), None)
        from core.storage.custom_cloudinary import CustomMediaCloudinaryStorage
        storage = CustomMediaCloudinaryStorage()
        storage_saved = storage.save('projects/test_storage_v3.png', png)
        storage_result = 'OK' if storage_saved == 'projects_test_storage_v3' else f'MISMATCH: got {storage_saved}'
    except Exception as e:
        storage_result = 'ERROR: ' + str(e)[:200]

    # Test 3: Via Django ORM
    orm_result = 'not tested'
    orm_stored = None
    orm_url = None
    try:
        Project.objects.filter(slug__startswith='test-v3-').delete()
        buf2 = io.BytesIO(png_data)
        png2 = InMemoryUploadedFile(buf2, 'image', 'test_orm.png', 'image/png', len(png_data), None)
        ts = int(time.time())
        project = Project.objects.create(
            title=f'Test V3 {ts}',
            slug=f'test-v3-{ts}',
            description='Test',
            short_description='Test',
            status='completed',
            featured=False,
            order=9999,
            image=png2,
        )
        project.refresh_from_db()
        orm_stored = str(project.image.name) if project.image else None
        orm_url = project.image.url if project.image else None

        if orm_stored and '/' not in orm_stored and '.' not in orm_stored:
            orm_result = 'OK - no slashes or extensions!'
        else:
            orm_result = f'PROBLEM: stored={orm_stored}'

        # Check URL
        if orm_url:
            import urllib.request
            try:
                req = urllib.request.Request(orm_url, method='HEAD')
                resp = urllib.request.urlopen(req, timeout=10)
                orm_result += f' URL=HTTP {resp.status}'
            except Exception as e:
                orm_result += f' URL error: {str(e)[:80]}'

        project.delete()
    except Exception as e:
        orm_result = 'ERROR: ' + str(e)[:200]

    return JsonResponse({
        'has_use_filename': has_use_filename,
        'upload_docstring': doc[:100],
        'direct_upload': {'result': direct_result, 'public_id': direct_pid},
        'storage_save': {'result': storage_result, 'saved_name': storage_saved},
        'orm_upload': {'result': orm_result, 'stored': orm_stored, 'url': orm_url},
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
