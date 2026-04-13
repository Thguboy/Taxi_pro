"""
ASGI config for taxi_site project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taxi_site.settings")

application = get_asgi_application()
