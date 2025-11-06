"""
ASGI config for teveclub_web project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teveclub_web.settings')

application = get_asgi_application()
