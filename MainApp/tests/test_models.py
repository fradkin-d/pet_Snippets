from django.test import TestCase
from MainApp.models import SupportedLang, Snippet, Comment, SnippetLike
from django.contrib.auth.models import User
import datetime as dt


class SupportedLangTest(TestCase):
    def setUp(self) -> None:
        self.lang = SupportedLang.objects.create(lang='Test')

    def test_supported_lang_max_length(self):
        max_length = self.lang._meta.get_field('lang').max_length
        self.assertEqual(max_length, 25)

    def test_supported_lang_str(self):
        self.assertEqual(self.lang.pk, str(self.lang))


class SnippetModelTest(TestCase):
    def setUp(self) -> None:
        self.test_user = User.objects.create_user('TestUser')
        self.test_lang = SupportedLang.objects.create(lang='TestLang')
        self.snippet = Snippet.objects.create(
            name='Test Snippet 1',
            lang=self.test_lang,
            code='print("Test code")',
            is_private=False,
            author=self.test_user
        )

    def test_name_max_length(self):
        max_length = self.snippet._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)

    def test_code_max_length(self):
        max_length = self.snippet._meta.get_field('code').max_length
        self.assertEqual(max_length, 5000)

    def test_slug_field(self):
        expected_date = (self.snippet.creation_date + dt.timedelta(hours=3)).strftime('%d-%m-%y-%H-%M-%S')
        expected_slug = 'test-snippet-1_' + expected_date
        self.assertEqual(self.snippet.slug, expected_slug)

    def test_to_dict_json(self):
        json = self.snippet.to_dict_json()
        expected_json = {
            'name': self.snippet.name,
            'lang': self.snippet.lang.lang,
            'creation_date': str(self.snippet.creation_date),
            'author': self.snippet.author.username,
            'like_count': self.snippet.snippetlike_set.count(),
            'comment_count': self.snippet.comment_set.count(),
            'is_private': self.snippet.is_private,
            'slug': self.snippet.slug,
        }
        self.assertEqual(json, expected_json)


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
