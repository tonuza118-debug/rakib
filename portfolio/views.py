"""Portfolio views - all data passed to the single-page 3D portfolio template."""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.db import models as django_models
from django.apps import apps
import cloudinary
import cloudinary.api
from django.conf import settings
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


@require_GET
def fix_cloudinary_images_view(request):
    """Temporary endpoint to fix broken Cloudinary image public_ids in the database.

    Visit https://rakib-payz.onrender.com/fix-images/ to run.
    Remove this view after use.
    """
    # Simple secret key check for basic protection
    secret = request.GET.get('key', '')
    if secret != 'fix-images-2026':
        return JsonResponse({'error': 'Unauthorized. Add ?key=fix-images-2026 to URL.'}, status=403)

    apply = request.GET.get('apply', '0') == '1'

    # Fetch all Cloudinary resources
    cloudinary_map = {}
    try:
        result = cloudinary.api.resources(type='upload', max_results=500)
        for r in result.get('resources', []):
            cloudinary_map[r['public_id']] = r['secure_url']
    except Exception as e:
        return JsonResponse({'error': f'Failed to fetch Cloudinary resources: {e}'}, status=500)

    # Build name lookup
    name_lookup = {}
    for pid in cloudinary_map:
        name_lookup[pid] = pid
        base = pid.rsplit('.', 1)[0] if '.' in pid else pid
        name_lookup[base] = pid
        if '/' in pid:
            filename = pid.rsplit('/', 1)[1]
            name_lookup[filename] = pid
            name_lookup[filename.rsplit('.', 1)[0] if '.' in filename else filename] = pid

    broken = []
    fixed = []
    ok_count = 0

    target_apps = ['portfolio', 'core']
    image_field_types = (django_models.ImageField, django_models.FileField)

    for app_label in target_apps:
        try:
            app_config = apps.get_app_config(app_label)
        except LookupError:
            continue
        for model in app_config.get_models():
            image_fields = [f.name for f in model._meta.get_fields()
                           if isinstance(f, image_field_types)]
            if not image_fields:
                continue
            for obj in model.objects.all():
                for field_name in image_fields:
                    stored_value = getattr(obj, field_name)
                    if not stored_value:
                        continue
                    stored_str = str(stored_value).strip()
                    if not stored_str:
                        continue

                    lookup_key = stored_str
                    lookup_no_ext = stored_str.rsplit('.', 1)[0] if '.' in stored_str else stored_str

                    exists = (
                        lookup_key in cloudinary_map or
                        lookup_no_ext in cloudinary_map or
                        lookup_key in name_lookup or
                        lookup_no_ext in name_lookup
                    )

                    if exists:
                        ok_count += 1
                        correct_pid = (
                            name_lookup.get(lookup_key) or
                            name_lookup.get(lookup_no_ext) or
                            lookup_key
                        )
                        if correct_pid != stored_str:
                            fixed.append({
                                'model': f'{app_label}.{model.__name__}',
                                'id': obj.pk,
                                'field': field_name,
                                'old': stored_str,
                                'new': correct_pid,
                                'url': cloudinary_map.get(correct_pid, 'N/A'),
                            })
                            if apply:
                                setattr(obj, field_name, correct_pid)
                                obj.save(update_fields=[field_name])
                    else:
                        # Try variations
                        found_match = None
                        variations = [
                            stored_str.replace('_', '-'),
                            stored_str.replace('-', '_'),
                            stored_str.replace('/', '_'),
                        ]
                        for v in variations:
                            if v in cloudinary_map:
                                found_match = v
                                break
                            if v in name_lookup:
                                found_match = name_lookup[v]
                                break

                        if not found_match:
                            stored_lower = stored_str.lower()
                            for pid in cloudinary_map:
                                if stored_lower in pid.lower():
                                    found_match = pid
                                    break

                        if found_match:
                            fixed.append({
                                'model': f'{app_label}.{model.__name__}',
                                'id': obj.pk,
                                'field': field_name,
                                'old': stored_str,
                                'new': found_match,
                                'url': cloudinary_map.get(found_match, 'N/A'),
                            })
                            if apply:
                                setattr(obj, field_name, found_match)
                                obj.save(update_fields=[field_name])
                        else:
                            broken.append({
                                'model': f'{app_label}.{model.__name__}',
                                'id': obj.pk,
                                'field': field_name,
                                'stored': stored_str,
                            })

    # Known manual fixes: DB value -> correct Cloudinary public_id
    # These are images where we can confidently match the DB value to the real public_id
    manual_fixes = {
        # Avatar: filename is the same, timestamp differs slightly
        'profile_WhatsApp_Image_2026-04-02_at_11_5Rmoe1a.28.00_PM':
            'profile_WhatsApp_Image_2026-04-02_at_10.28.02_AM_1',
        # Avatar also has a folder-based version in Cloudinary
        'profile_WhatsApp_Image_2026-04-02_at_11_5Rmoe1a.28.00_PM_1':
            'profile_WhatsApp_Image_2026-04-02_at_10.28.02_AM_1',
    }

    manual_fixed = []
    if apply:
        for app_label in target_apps:
            try:
                app_config = apps.get_app_config(app_label)
            except LookupError:
                continue
            for model in app_config.get_models():
                image_fields = [f.name for f in model._meta.get_fields()
                               if isinstance(f, image_field_types)]
                for obj in model.objects.all():
                    for field_name in image_fields:
                        stored = str(getattr(obj, field_name, '') or '').strip()
                        if stored in manual_fixes:
                            correct = manual_fixes[stored]
                            setattr(obj, field_name, correct)
                            obj.save(update_fields=[field_name])
                            manual_fixed.append({
                                'model': f'{app_label}.{model.__name__}',
                                'id': obj.pk,
                                'field': field_name,
                                'old': stored,
                                'new': correct,
                                'url': cloudinary_map.get(correct, 'N/A'),
                            })

    return JsonResponse({
        'status': 'complete',
        'mode': 'APPLIED' if apply else 'DRY RUN',
        'ok': ok_count,
        'auto_fixed': len(fixed),
        'manual_fixed': len(manual_fixed),
        'broken': len(broken),
        'auto_fixed_details': fixed,
        'manual_fixed_details': manual_fixed,
        'broken_details': broken,
        'message': (
            f'{len(fixed)} auto-fixed, {len(manual_fixed)} manually matched, '
            f'{len(broken)} need re-upload (not in Cloudinary).'
        )
    }, json_dumps_params={'indent': 2})
