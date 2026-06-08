"""Upload all local media files to Cloudinary."""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
import cloudinary
import cloudinary.uploader
from decouple import config


class Command(BaseCommand):
    help = 'Upload all local media files to Cloudinary'

    def handle(self, *args, **options):
        # Configure Cloudinary from .env
        cloud_name = config('CLOUDINARY_CLOUD_NAME', default='')
        api_key = config('CLOUDINARY_API_KEY', default='')
        api_secret = config('CLOUDINARY_API_SECRET', default='')

        if not cloud_name:
            self.stdout.write(self.style.ERROR('Cloudinary credentials not set in .env file.'))
            return

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
        )

        media_root = settings.MEDIA_ROOT
        uploaded = 0
        skipped = 0

        for root, dirs, files in os.walk(media_root):
            for filename in files:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, media_root)

                # Build Cloudinary public_id from relative path
                public_id = rel_path.replace('\\', '/').replace('/', '_').rsplit('.', 1)[0]

                try:
                    result = cloudinary.uploader.upload(
                        filepath,
                        public_id=public_id,
                        overwrite=True,
                        resource_type='image',
                    )
                    uploaded += 1
                    self.stdout.write(f'  [OK] {rel_path}')
                    self.stdout.write(f'       URL: {result["secure_url"]}')
                except Exception as e:
                    skipped += 1
                    self.stdout.write(f'  [SKIP] {rel_path}: {e}')

        self.stdout.write(f'\nDone! Uploaded: {uploaded}, Skipped: {skipped}')
