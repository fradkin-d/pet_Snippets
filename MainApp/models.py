from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import datetime as dt


class SupportedLang(models.Model):
    lang = models.CharField(max_length=25, primary_key=True)

    def __str__(self):
        return self.lang


class Snippet(models.Model):
    name = models.CharField(max_length=100)
    lang = models.ForeignKey(SupportedLang, on_delete=models.CASCADE)
    description = models.CharField(max_length=250, default='')
    code = models.TextField(max_length=5000)
    creation_date = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, default=None, max_length=150)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = '_'.join((slugify(self.name), dt.datetime.now().strftime('%d-%m-%y-%H-%M-%S')))
        super().save(*args, **kwargs)

    def to_dict_json(self):
        return {
            'name': self.name,
            'lang': self.lang.lang,
            'creation_date': str(self.creation_date),
            'author': self.author.username,
            'like_count': self.snippetlike_set.count(),
            'comment_count': self.comment_set.count(),
            'is_private': self.is_private,
            'slug': self.slug,
        }


class Comment(models.Model):
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField(max_length=250)


class SnippetLike(models.Model):
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
