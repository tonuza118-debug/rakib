"""Vercel serverless function — Django WSGI wrapper."""
import os
import sys

# Add project root to Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_project.settings')

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
