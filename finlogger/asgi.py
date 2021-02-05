"""
ASGI config for finlogger project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finlogger.settings')

application = get_asgi_application()

import re
filename = 'aa'
re.compile(r'([\s*\d+\s*\/\s*\d+\s*\n\n]*'
           r'[[-]*\s*Page\s*\d+[-]*\n\n]*'
           r'ProSecure\s+'
           f'{filename})')