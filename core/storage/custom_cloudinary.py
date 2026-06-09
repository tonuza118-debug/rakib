"""Custom Cloudinary storage that uses underscores instead of slashes in public_ids."""
import os
import cloudinary
import cloudinary.uploader
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.conf import settings


class CustomMediaCloudinaryStorage(MediaCloudinaryStorage):
    """
    Custom Cloudinary storage that replaces slashes with underscores in public_ids.

    django-cloudinary-storage creates folder-based public_ids like: projects/gallery/filename.jpg
    This custom storage converts them to: projects_gallery_filename

    The key fix: the actual public_id returned by Cloudinary's upload response is stored
    in the database, and the url() method returns the raw (untransformed) Cloudinary URL.
    """

    def _upload(self, name, content):
        """Upload file to Cloudinary with underscored public_id."""
        # Build a clean public_id from the file path:
        # e.g. "projects/gallery/my_photo.jpg" -> "projects_gallery_my_photo"
        public_id = name.replace('/', '_')
        if '.' in public_id:
            public_id = public_id.rsplit('.', 1)[0]

        # Normalize: collapse multiple underscores, strip leading/trailing
        while '__' in public_id:
            public_id = public_id.replace('__', '_')
        public_id = public_id.strip('_')

        options = {
            'public_id': public_id,
            'use_filename': False,
            'unique_filename': False,
            'resource_type': self._get_resource_type(name),
            'tags': self.TAG,
            'invalidate': True,
        }

        response = cloudinary.uploader.upload(content, **options)

        return response

    def _save(self, name, content):
        """Save file to Cloudinary and return the stored public_id.

        The stored value (public_id) is what goes into the database,
        and what url() will later receive to build the image URL.
        """
        name = self._normalise_name(name)
        response = self._upload(name, content)

        # Use the ACTUAL public_id from Cloudinary's response — not our computed one.
        # This ensures the db value is guaranteed to match Cloudinary's record.
        actual_public_id = response['public_id']

        return actual_public_id

    def url(self, name):
        """Return the raw (untransformed) Cloudinary image URL.

        No transformations — just the original image as uploaded.
        """
        if not name:
            return ''

        # Already a full URL — return directly
        if isinstance(name, str) and name.startswith('http'):
            return name

        public_id = name

        # Legacy data: convert slashes to underscores
        if '/' in public_id:
            public_id = public_id.replace('/', '_')

        # Legacy data: remove file extension if present
        if '.' in public_id:
            public_id = public_id.rsplit('.', 1)[0]

        cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', '')
        return f'https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}'

    def get_valid_name(self, name):
        """Return the name suitable for storage (underscored, no slashes)."""
        return name.replace('/', '_') if name else name
# Cache bust: Tue Jun  9 02:46:59 BST 2026
# Build: fac30a1672f18880543f7592d784cd8bca14e99b
