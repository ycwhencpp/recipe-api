from .base import *


DEBUG = False
ALLOWED_HOSTS = [
    '*',
    'localhost'
    ,'127.0.0.1'
    ]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# If your entire site is served over HTTPS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
