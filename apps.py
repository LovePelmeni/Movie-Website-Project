import logging.handlers
from logging import Formatter
from django.apps import AppConfig
from django.conf import settings

class MovieConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movie'

    def ready(self):
        from . import signals



