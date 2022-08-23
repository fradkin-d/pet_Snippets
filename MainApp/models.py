from django.db import models
from django.contrib.auth.models import User


class SupportedLang(models.Model):
    lang = models.CharField(max_length=25, primary_key=True)

    def __str__(self):
        return self.lang


class Snippet(models.Model):
    name = models.CharField(max_length=100)
    lang = models.ForeignKey(SupportedLang, on_delete=models.CASCADE)
    code = models.TextField(max_length=5000)
    creation_date = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
