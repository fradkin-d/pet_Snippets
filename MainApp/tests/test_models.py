from django.test import TestCase
from MainApp.models import SupportedLang, Snippet, Comment, SnippetLike
from django.contrib.auth.models import User
import datetime as dt


class SupportedLangTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        SupportedLang.objects.create(lang='Test')

    def test_supported_lang_max_length(self):
        supported_lang = SupportedLang.objects.get(lang='Test')
        max_length = supported_lang._meta.get_field('lang').max_length
        self.assertEqual(max_length, 25)

    def test_supported_lang_str(self):
        supported_lang = SupportedLang.objects.get(lang='Test')
        self.assertEqual(supported_lang.pk, str(supported_lang))


class SnippetModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user('TestUser')
        test_lang = SupportedLang.objects.create(lang='TestLang')
        Snippet.objects.create(
            name='Test Snippet 1',
            lang=test_lang,
            code='print("Test code")',
            is_private=False,
            author=test_user
        )

    def test_name_max_length(self):
        snippet = Snippet.objects.get(id=1)
        max_length = snippet._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)

    def test_code_max_length(self):
        snippet = Snippet.objects.get(id=1)
        max_length = snippet._meta.get_field('code').max_length
        self.assertEqual(max_length, 5000)

    def test_slug_field(self):
        snippet = Snippet.objects.get(id=1)
        slug = snippet.slug
        expected_date = (snippet.creation_date + dt.timedelta(hours=3)).strftime('%d-%m-%y-%H-%M-%S')
        expected_slug = 'test-snippet-1_' + expected_date
        self.assertEqual(slug, expected_slug)

    def test_to_dict_json(self):
        snippet = Snippet.objects.get(id=1)
        snippet.like_count = 0
        snippet.comment_count = 0
        json = snippet.to_dict_json()
        expected_json = {
            'name': snippet.name,
            'lang': snippet.lang.lang,
            'creation_date': str(snippet.creation_date),
            'author': snippet.author.username,
            'like_count': snippet.like_count,
            'comment_count': snippet.comment_count,
            'is_private': snippet.is_private,
            'slug': snippet.slug,
        }
        self.assertEqual(json, expected_json)


class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user('TestUser')
        test_lang = SupportedLang.objects.create(lang='TestLang')
        test_snippet = Snippet.objects.create(
            name='Test Snippet 1',
            lang=test_lang,
            code='print("Test code")',
            is_private=False,
            author=test_user
        )
        Comment.objects.create(
            snippet=test_snippet,
            author=test_user,
            text='Test Comment'
        )

    def test_text_max_length(self):
        comment = Comment.objects.get(id=1)
        max_length = comment._meta.get_field('text').max_length
        self.assertEqual(max_length, 250)

    def test_snippet_have_comment(self):
        snippet = Snippet.objects.get(id=1)
        snippet_comments_count = snippet.comment_set.count()
        self.assertEqual(snippet_comments_count, 1)


class SnippetLikeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user('TestUser')
        test_lang = SupportedLang.objects.create(lang='TestLang')
        test_snippet = Snippet.objects.create(
            name='Test Snippet 1',
            lang=test_lang,
            code='print("Test code")',
            is_private=False,
            author=test_user
        )
        SnippetLike.objects.create(
            snippet=test_snippet,
            author=test_user
        )

    def test_snippet_have_like(self):
        snippet = Snippet.objects.get(id=1)
        snippet_likes_count = snippet.snippetlike_set.count()
        self.assertEqual(snippet_likes_count, 1)
