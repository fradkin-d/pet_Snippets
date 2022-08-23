from django.contrib import admin
from .models import Snippet, SupportedLang

admin.site.register(Snippet)
admin.site.register(SupportedLang)
