from django.contrib.auth.models import User
from django.db import models

from Comments.models import Comment
from MainApp.models import Snippet


class SnippetLike(models.Model):
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
