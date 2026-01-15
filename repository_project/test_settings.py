"""
Test settings for repository_project - uses SQLite for testing
"""
from .settings import *

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Remove whitenoise middleware for testing
MIDDLEWARE = [m for m in MIDDLEWARE if 'whitenoise' not in m.lower()]

