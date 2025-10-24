"""
WSGI config for apex_graph project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apex_graph.settings')

application = get_wsgi_application()
