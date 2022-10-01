from django.test import TestCase

from Comments.models import Comment
from MainApp.models import SupportedLang, Snippet
from django.contrib.auth.models import User


class CommentModelTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user('TestUser')
        self.lang = SupportedLang.objects.create(lang='TestLang')
        self.snippet = Snippet.objects.create(
            name='Test Snippet 1',
            lang=self.lang,
            code='print("Test code")',
            is_private=False,
            author=self.user
        )
        self.comment = Comment.objects.create(
            snippet=self.snippet,
            author=self.user,
            text='Test Comment'
        )

    def test_text_max_length(self):
        max_length = self.comment._meta.get_field('text').max_length
        self.assertEqual(max_length, 250)
