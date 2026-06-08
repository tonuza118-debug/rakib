"""Custom Cloudinary storage that uses underscores instead of slashes in public_ids."""
import os
import cloudinary
import cloudinary.uploader
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.core.files.uploadedfile import UploadedFile


class CustomMediaCloudinaryStorage(MediaCloudinaryStorage):
    """
    Custom Cloudinary storage that replaces slashes with underscores in public_ids.
    django-cloudinary-storage creates folder-based public_ids like: projects/gallery/filename.jpg
    This custom storage converts them to: projects_gallery_filename
    """

    def _upload(self, name, content):
        options = {
            'use_filename': True,
            'resource_type': self._get_resource_type(name),
            'tags': self.TAG,
            'invalidate': True,
        }
        # Build a clean public_id: replace slashes with underscores, remove extension
        public_id = name.replace('/', '_')
        if '.' in public_id:
            public_id = public_id.rsplit('.', 1)[0]
        options['public_id'] = public_id
        response = cloudinary.uploader.upload(content, **options)
        return response

    def _save(self, name, content):
        """Save file to Cloudinary and return the clean public_id."""
        name = self._normalise_name(name)
        content = UploadedFile(content, name)
        response = self._upload(name, content)
        return response['public_id']

    def url(self, name):
        """Generate Cloudinary URL from public_id."""
        base = self._get_prefix()
        return f'{base}{name}'
