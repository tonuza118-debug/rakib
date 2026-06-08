"""Update all model image fields to match exact Cloudinary public_ids."""
import cloudinary
import cloudinary.api
from django.core.management.base import BaseCommand
from portfolio.models import Profile, Project, ProjectImage, Testimonial, BlogPost, Achievement, Experience, Education, Publication
from core.models import SiteSettings


class Command(BaseCommand):
    help = 'Update model image fields to match exact Cloudinary public_ids'

    def handle(self, *args, **options):
        cloudinary.config(
            cloud_name='dwcazkqlm',
            api_key='112936847494325',
            api_secret='RuGdHTx9EZVYpASgkt0UJub8504',
        )

        # Build a map of Cloudinary public_ids
        result = cloudinary.api.resources(type='upload', max_results=100)
        cloudinary_ids = {r['public_id'] for r in result['resources']}
        self.stdout.write(f'Found {len(cloudinary_ids)} files in Cloudinary')

        updated = 0

        # Helper to find matching Cloudinary public_id
        def find_cloudinary_id(local_name):
            # Try exact match first
            if local_name in cloudinary_ids:
                return local_name
            # Try without extension
            no_ext = local_name.rsplit('.', 1)[0] if '.' in local_name else local_name
            if no_ext in cloudinary_ids:
                return no_ext
            # Try with common extensions
            for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.JPG', '.JPEG', '.PNG']:
                candidate = no_ext + ext
                if candidate in cloudinary_ids:
                    return candidate
            # Try matching by filename
            filename = local_name.split('/')[-1] if '/' in local_name else local_name
            for cid in cloudinary_ids:
                if cid.endswith(filename) or cid.endswith(no_ext):
                    return cid
            return None

        # Update Profile avatars
        for p in Profile.objects.all():
            if p.avatar and p.avatar.name:
                cid = find_cloudinary_id(p.avatar.name)
                if cid and cid != p.avatar.name:
                    p.avatar.name = cid
                    p.save(update_fields=['avatar'])
                    updated += 1
                    self.stdout.write(f'  [OK] Profile: {p.avatar.name}')

        # Update Project images
        for p in Project.objects.all():
            if p.image and p.image.name:
                cid = find_cloudinary_id(p.image.name)
                if cid and cid != p.image.name:
                    p.image.name = cid
                    p.save(update_fields=['image'])
                    updated += 1
                    self.stdout.write(f'  [OK] Project: {p.image.name}')

        # Update ProjectImage
        for pi in ProjectImage.objects.all():
            if pi.image and pi.image.name:
                cid = find_cloudinary_id(pi.image.name)
                if cid and cid != pi.image.name:
                    pi.image.name = cid
                    pi.save(update_fields=['image'])
                    updated += 1
                    self.stdout.write(f'  [OK] ProjectImage: {pi.image.name}')

        # Update Achievement images
        for a in Achievement.objects.all():
            if a.image and a.image.name:
                cid = find_cloudinary_id(a.image.name)
                if cid and cid != a.image.name:
                    a.image.name = cid
                    a.save(update_fields=['image'])
                    updated += 1
                    self.stdout.write(f'  [OK] Achievement: {a.image.name}')

        # Update Experience logos
        for e in Experience.objects.all():
            if e.company_logo and e.company_logo.name:
                cid = find_cloudinary_id(e.company_logo.name)
                if cid and cid != e.company_logo.name:
                    e.company_logo.name = cid
                    e.save(update_fields=['company_logo'])
                    updated += 1
                    self.stdout.write(f'  [OK] Experience: {e.company_logo.name}')

        # Update Education logos
        for e in Education.objects.all():
            if e.logo and e.logo.name:
                cid = find_cloudinary_id(e.logo.name)
                if cid and cid != e.logo.name:
                    e.logo.name = cid
                    e.save(update_fields=['logo'])
                    updated += 1
                    self.stdout.write(f'  [OK] Education: {e.logo.name}')

        # Update SiteSettings
        for s in SiteSettings.objects.all():
            if s.logo and s.logo.name:
                cid = find_cloudinary_id(s.logo.name)
                if cid and cid != s.logo.name:
                    s.logo.name = cid
                    s.save(update_fields=['logo'])
                    updated += 1
                    self.stdout.write(f'  [OK] SiteSettings logo: {s.logo.name}')
            if s.favicon and s.favicon.name:
                cid = find_cloudinary_id(s.favicon.name)
                if cid and cid != s.favicon.name:
                    s.favicon.name = cid
                    s.save(update_fields=['favicon'])
                    updated += 1
                    self.stdout.write(f'  [OK] SiteSettings favicon: {s.favicon.name}')

        self.stdout.write(f'\nDone! Updated {updated} image fields.')
