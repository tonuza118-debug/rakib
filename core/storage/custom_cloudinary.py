"""Custom Cloudinary storage that uses underscores instead of slashes in public_ids."""
import os
import cloudinary
from cloudinary_storage.storage import MediaCloudinaryStorage


class CustomMediaCloudinaryStorage(MediaCloudinaryStorage):
    """
    Custom Cloudinary storage that replaces slashes with underscores in public_ids.

    By default, django-cloudinary-storage creates folder-based public_ids like:
        projects/gallery/filename.jpg

    This custom storage converts them to:
        projects_gallery_filename.jpg

    This ensures consistent URL formatting and avoids broken image URLs.
    """

    def _upload(self, name, content):
        options = {
            'use_filename': True,
            'resource_type': self._get_resource_type(name),
            'tags': self.TAG,
        }
        # Use the full path with underscores instead of folder structure
        # e.g., "projects/gallery/image.jpg" → "projects_gallery_image"
        public_id = name.replace('/', '_')
        # Remove file extension from public_id (Cloudinary adds it automatically)
        if '.' in public_id:
            public_id = public_id.rsplit('.', 1)[0]
        options['public_id'] = public_id
        return cloudinary.uploader.upload(content, **options)
