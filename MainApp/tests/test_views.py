from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from AJAX.models import SnippetLike
from Comments.models import Comment
from MainApp.models import Snippet, SupportedLang


class IndexPageViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user('TestUser')
        self.lang = SupportedLang.objects.create(lang='TestLang')

        number_of_public_snippets = 15
        for snippet_num in range(number_of_public_snippets):
            Snippet.objects.create(
                name=f'Test Snippet {snippet_num}',
                lang=self.lang,
                code='print("Test code")',
                is_private=False,
                author=self.user
            )

        for snippet in Snippet.objects.filter(is_private=False):
            SnippetLike.objects.create(snippet=snippet, author=self.user)
            Comment.objects.create(snippet=snippet, author=self.user, text='Test text')

        number_of_private_snippets = 5
        for snippet_num in range(number_of_private_snippets):
            Snippet.objects.create(
                name=f'Test Private Snippet {snippet_num}',
                lang=self.lang,
                code='print("Test code")',
                is_private=True,
                author=self.user
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/index.html')

    def test_view_have_full_context(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pagename' in response.context)
        self.assertTrue('snippets_count' in response.context)
        self.assertTrue('top_ten_by_rating' in response.context)
        self.assertTrue('top_ten_by_reviews' in response.context)

    def test_list_top_ten_by_rating(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['top_ten_by_rating']) == 10)

    def test_list_top_ten_by_reviews(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['top_ten_by_reviews']) == 10)


class SnippetCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='TestUser', password='Pa55w.rd')
        self.lang = SupportedLang.objects.create(lang='TestLang')

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get('/snippets/add')
        self.assertRedirects(response, '/accounts/login/?next=/snippets/add')

    def test_view_logged_in_url_exists_at_desired_location(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get('/snippets/add')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('add_snippet_page'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('add_snippet_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/add_snippet.html')

    def test_view_validation(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('add_snippet_page'))
        self.assertEqual(response.status_code, 200)
        self.client.post(
            reverse('add_snippet_page'),
            data={
                'name': 'TestName',
                'lang': self.lang,
                'code': 'TestCode',
                'is_private': False
            },
            follow=True
        )
        self.assertTrue(Snippet.objects.filter(author=self.user).exists())

    def test_view_success_redirect(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('add_snippet_page'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('add_snippet_page'),
            data={
                'name': 'TestName',
                'lang': self.lang,
                'code': 'TestCode',
                'is_private': False
            },
            follow=True
        )
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        self.assertTrue('Сниппет добавлен' in message.message)


class SnippetUpdateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='TestUser', password='Pa55w.rd')
        self.lang = SupportedLang.objects.create(lang='TestLang')
        self.snippet = Snippet.objects.create(
            name='TestName',
            lang=self.lang,
            code='TestCode',
            description='TestDescription',
            is_private=False,
            author=self.user
        )

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(f'/snippets/{self.snippet.slug}/update', follow=True)
        self.assertRedirects(response, f'/accounts/login/?next=/snippets/{self.snippet.slug}/update')

    def test_view_logged_in_url_exists_at_desired_location(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(f'/snippets/{self.snippet.slug}/update')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('snippet_update_page', kwargs={'slug': self.snippet.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('snippet_update_page', kwargs={'slug': self.snippet.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/snippet_update.html')

    def test_view_success_redirect(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(f'/snippets/{self.snippet.slug}/update?next=/snippets/{self.snippet.slug}')
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            f'/snippets/{self.snippet.slug}/update?next=/snippets/{self.snippet.slug}',
            data={
                'name': 'TestNameUpdated',
                'description': 'TestDescription',
                'lang': self.lang,
                'code': 'TestCodeUpdated',
                'is_private': False
            },
            follow=True
        )
        self.assertRedirects(response, f'/snippets/{self.snippet.slug}')
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        self.assertTrue("Сниппет обновлен" in message.message)


class SnippetDeleteViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='TestUser', password='Pa55w.rd')
        self.lang = SupportedLang.objects.create(lang='TestLang')
        self.snippet = Snippet.objects.create(
            name='TestName',
            lang=self.lang,
            code='TestCode',
            is_private=False,
            author=self.user
        )

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(f'/snippets/{self.snippet.slug}/delete', follow=True)
        self.assertRedirects(response, f'/accounts/login/?next=/snippets/{self.snippet.slug}/delete')

    def test_view_logged_in_url_exists_at_desired_location(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(f'/snippets/{self.snippet.slug}/delete')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('snippet_delete_page', kwargs={'slug': self.snippet.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('snippet_delete_page', kwargs={'slug': self.snippet.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/snippet_delete.html')

    def test_view_success_redirect(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('snippet_delete_page', kwargs={'slug': self.snippet.slug}))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('snippet_delete_page', kwargs={'slug': self.snippet.slug}),
            follow=True
        )
        self.assertRedirects(response, '/snippets/my_list')

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        self.assertTrue("Сниппет удален" in message.message)


class SnippetDetailViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='TestUser', password='Pa55w.rd')
        self.lang = SupportedLang.objects.create(lang='TestLang')
        self.snippet = Snippet.objects.create(
            name='TestName',
            lang=self.lang,
            code='TestCode',
            is_private=False,
            author=self.user
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/snippets/{self.snippet.slug}')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('snippet_detail_page', kwargs={'slug': self.snippet.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('snippet_detail_page', kwargs={'slug': self.snippet.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/snippet_detail.html')

    def test_view_anon_user_have_full_context(self):
        response = self.client.get(reverse('snippet_detail_page', kwargs={'slug': self.snippet.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pagename' in response.context)
        self.assertTrue('user' in response.context)
        self.assertTrue('comment_form' in response.context)
        self.assertTrue('anon_user' in response.context)
        self.assertFalse('is_liked' in response.context)

    def test_view_logged_in_have_full_context(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('snippet_detail_page', kwargs={'slug': self.snippet.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pagename' in response.context)
        self.assertTrue('user' in response.context)
        self.assertTrue('comment_form' in response.context)
        self.assertTrue('anon_user' in response.context)
        self.assertTrue('is_liked' in response.context)


class SnippetsListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/snippets/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('snippets_list_page'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('snippets_list_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/snippet_list.html')

    def test_view_have_full_context(self):
        response = self.client.get(reverse('snippets_list_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pagename' in response.context)


class UserSnippetsListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/snippets/my_list')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('my_snippets_list_page'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('my_snippets_list_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/my_snippet_list.html')

    def test_view_have_full_context(self):
        response = self.client.get(reverse('my_snippets_list_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pagename' in response.context)
