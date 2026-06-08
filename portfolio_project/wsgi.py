"""
WSGI config for portfolio_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import importlib

# Clear stale .pyc cache to prevent old code from being loaded
# Render's build process doesn't clear __pycache__ between deploys
_base_dir = os.path.dirname(os.path.abspath(__file__))
for root, dirs, files in os.walk(_base_dir):
    if '__pycache__' in dirs:
        import shutil
        cache_dir = os.path.join(root, '__pycache__')
        try:
            shutil.rmtree(cache_dir)
        except OSError:
            pass

# Remove cached storage module to force reimport with fresh .py
for mod_name in list(sys.modules):
    if 'cloudinary_storage' in mod_name or 'custom_cloudinary' in mod_name:
        del sys.modules[mod_name]

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_project.settings')

application = get_wsgi_application()
