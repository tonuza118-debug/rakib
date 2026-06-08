"""
Management command to fix broken Cloudinary image references in the database.

Some images were stored with incorrect public_ids by previous versions of the
custom storage. This command:

1. Scans all ImageField / FileField values in the database
2. Checks whether the stored public_id actually exists in Cloudinary
3. Tries to find the correct public_id by searching Cloudinary
4. Updates the database if a match is found

Usage:
    python manage.py fix_cloudinary_images          # Dry run (show what would change)
    python manage.py fix_cloudinary_images --apply   # Actually apply fixes
"""

from django.core.management.base import BaseCommand
from django.db import models
from django.apps import apps
import cloudinary
import cloudinary.api
from django.conf import settings


class Command(BaseCommand):
    help = "Fix broken Cloudinary image public_ids stored in the database"

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually apply the fixes (default is dry-run)',
        )

    def handle(self, *args, **options):
        apply = options['apply']

        # Build Cloudinary resource lookup
        self.stdout.write("Fetching all resources from Cloudinary...")
        cloudinary_map = {}  # public_id -> secure_url
        try:
            result = cloudinary.api.resources(type='upload', max_results=500)
            for r in result.get('resources', []):
                cloudinary_map[r['public_id']] = r['secure_url']
            self.stdout.write(f"  Found {len(cloudinary_map)} resources in Cloudinary")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Error fetching Cloudinary resources: {e}"))
            return

        # Also build a lookup by filename (without extension, without folder)
        # This helps match old DB values to actual public_ids
        name_lookup = {}  # normalized_name -> public_id
        for pid in cloudinary_map:
            # Key by the full public_id
            name_lookup[pid] = pid
            # Key by filename without extension
            base = pid.rsplit('.', 1)[0] if '.' in pid else pid
            name_lookup[base] = pid
            # Key by just the filename part (after last /)
            if '/' in pid:
                filename = pid.rsplit('/', 1)[1]
                name_lookup[filename] = pid
                name_lookup[filename.rsplit('.', 1)[0] if '.' in filename else filename] = pid

        # Find all ImageField and FileField in our models
        broken = []
        fixed = []
        ok_count = 0

        target_apps = ['portfolio', 'core']

        for app_label in target_apps:
            app_config = apps.get_app_config(app_label)
            for model in app_config.get_models():
                image_fields = []
                for field in model._meta.get_fields():
                    if isinstance(field, (models.ImageField, models.FileField)):
                        image_fields.append(field.name)

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

                        # The stored value is the public_id (not a full URL)
                        # Strip any file extension for comparison
                        lookup_key = stored_str
                        lookup_no_ext = stored_str.rsplit('.', 1)[0] if '.' in stored_str else stored_str

                        # Check if it exists in Cloudinary (try multiple forms)
                        exists = (
                            lookup_key in cloudinary_map or
                            lookup_no_ext in cloudinary_map or
                            lookup_key in name_lookup or
                            lookup_no_ext in name_lookup
                        )

                        if exists:
                            ok_count += 1
                            # Find the correct public_id
                            correct_pid = (
                                name_lookup.get(lookup_key) or
                                name_lookup.get(lookup_no_ext) or
                                lookup_key
                            )
                            if correct_pid != stored_str:
                                # The stored value is close but not exact
                                fixed.append({
                                    'model': f'{app_label}.{model.__name__}',
                                    'id': obj.pk,
                                    'field': field_name,
                                    'old': stored_str,
                                    'new': correct_pid,
                                })
                                if apply:
                                    setattr(obj, field_name, correct_pid)
                                    obj.save(update_fields=[field_name])
                        else:
                            # Try to find a match by searching different name variations
                            found_match = None

                            # Try underscore.replace('-') and vice versa
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

                            # Try matching by filename fragment
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

        # Report
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"OK: {ok_count} images have correct public_ids"))
        self.stdout.write("")

        if fixed:
            self.stdout.write(self.style.WARNING(f"NEEDS FIX: {len(fixed)} images have fixable public_ids:"))
            self.stdout.write("")
            for item in fixed:
                status = "FIXED" if apply else "WOULD FIX"
                self.stdout.write(f"  [{status}] {item['model']} id={item['id']} {item['field']}")
                self.stdout.write(f"    Old: {item['old']}")
                self.stdout.write(f"    New: {item['new']}")
                url = cloudinary_map.get(item['new'], 'N/A')
                self.stdout.write(f"    URL: {url}")
                self.stdout.write("")

        if broken:
            self.stdout.write(self.style.ERROR(f"BROKEN: {len(broken)} images not found in Cloudinary (need re-upload):"))
            self.stdout.write("")
            for item in broken:
                self.stdout.write(f"  {item['model']} id={item['id']} {item['field']}")
                self.stdout.write(f"    Stored: {item['stored']}")
                self.stdout.write("")

        if not apply and (fixed or broken):
            self.stdout.write(self.style.WARNING("This was a DRY RUN. Use --apply to fix the DB values."))
        elif apply and fixed:
            self.stdout.write(self.style.SUCCESS(f"Applied {len(fixed)} fixes to the database."))
