"""
WSGI config for apps project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# 设置默认的环境变量，ci发布的时候可以设置环境变量替换
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings.prod')

application = get_wsgi_application()
