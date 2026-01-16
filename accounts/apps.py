from django.apps import AppConfig
from django.contrib import admin


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        admin.site.site_header = "COMSOC Administration"
        admin.site.site_title = "COMSOC Administration"
        admin.site.index_title = "COMSOC Administration"
