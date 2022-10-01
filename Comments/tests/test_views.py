from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from Comments.models import Comment
from MainApp.models import Snippet, SupportedLang


class CreateCommentViewTest(TestCase):
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
        response = self.client.get('/comment/create', follow=True)
        self.assertRedirects(response, '/accounts/login/')

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.post('/comment/create', {'snippet': self.snippet.id, 'text': 'TestText'}, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.post(reverse('create_comment'), {
            'snippet': self.snippet.id, 'text': 'TestText'
        }, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_create_comment(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        self.client.post(reverse('create_comment'), {'snippet': self.snippet.id, 'text': 'TestText'})
        self.assertTrue(Comment.objects.filter(snippet=self.snippet).exists())


class DeleteCommentViewTest(TestCase):
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
        self.comment = Comment.objects.create(
            snippet=self.snippet,
            author=self.user,
            text='TestText'
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(f'/comment/delete/{self.comment.id}', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('delete_comment', kwargs={'pk': self.comment.id}), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_delete_comment(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        self.client.get(reverse('delete_comment', kwargs={'pk': self.comment.id}))
        self.assertFalse(Comment.objects.filter(snippet=self.snippet).exists())
