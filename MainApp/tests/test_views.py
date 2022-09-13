from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from MainApp.models import Snippet, SupportedLang, SnippetLike, Comment
import json


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


class RegistrationViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/accounts/registration/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/registration.html')

    def test_view_have_full_context(self):
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pagename' in response.context)
        self.assertTrue('form' in response.context)

    def test_registration_success_message(self):
        response = self.client.post(
            reverse('registration'),
            data={
                'username': 'TestUser',
                'email': 'test@mail.com',
                'password1': 'Pa55w.rd',
                'password2': 'Pa55w.rd'
            },
            follow=True
        )
        self.assertRedirects(response, reverse('home'))

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        self.assertTrue("Регистрация прошла успешно!" in message.message)

    def test_registration_failure_message(self):
        response = self.client.post(
            reverse('registration'),
            data={
                'username': 'TestUser',
                'email': 'test@mail.com',
                'password1': 'Pa55w.rd',
                'password2': 'Pa55w,rd'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-danger")
        self.assertTrue("Ошибка регистрации! Проверьте правильность заполнения формы" in message.message)


class LoginViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/login.html')

    def test_view_have_full_context(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pagename' in response.context)

    def test_login_success_message(self):
        User.objects.create_user(username='TestUser', password='Pa55w.rd')

        response = self.client.post(
            reverse('login'),
            data={
                'username': 'TestUser',
                'password': 'Pa55w.rd'
            },
            follow=True
        )
        self.assertRedirects(response, reverse('home'))

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        self.assertTrue(f'Добро пожаловать, TestUser!' in message.message)

    def test_login_failure_message(self):
        response = self.client.post(
            reverse('login'),
            data={
                'username': 'TestUser',
                'password': 'Pa55w,rd'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-danger")
        self.assertTrue('Ошибка входа! Проверьте правильность заполнения формы' in message.message)


class LogoutViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/accounts/logout/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_logout_message(self):
        response = self.client.post(
            reverse('login'),
            data={
                'username': 'TestUser',
                'password': 'Pa55w,rd'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        self.assertTrue('Выполнен выход' in message.message)


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
        self.assertRedirects(response, '/snippets/my_list')
        Snippet.objects.filter(author=self.user).exists()
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
        self.assertRedirects(response, '/snippets/my_list')

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
        response = self.client.get(reverse('snippet_update_page', kwargs={'slug': self.snippet.slug}))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('snippet_update_page', kwargs={'slug': self.snippet.slug}),
            data={
                'name': 'TestNameUpdated',
                'lang': self.lang,
                'code': 'TestCodeUpdated',
                'is_private': False
            },
            follow=True
        )
        self.assertRedirects(response, '/snippets/my_list')

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


class SnippetJsonNonPrivateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='TestUser', password='Pa55w.rd')
        self.lang = SupportedLang.objects.create(lang='TestLang')
        self.snippet_1 = Snippet.objects.create(
            name='TestName 1',
            lang=self.lang,
            code='TestCode 1',
            is_private=False,
            author=self.user
        )
        self.snippet_2 = Snippet.objects.create(
            name='TestName 2',
            lang=self.lang,
            code='TestCode 2',
            is_private=False,
            author=self.user
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/ajax/snippet_non_private/json')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('snippet_non_private_json'))
        self.assertEqual(response.status_code, 200)

    def test_json_response(self):
        snippets = Snippet.objects.all()
        json_response = self.client.get(reverse('snippet_non_private_json'))

        json_response_params = json.loads(json_response.content).keys()
        self.assertTrue('data' in json_response_params)
        self.assertTrue('recordsTotal' in json_response_params)
        self.assertTrue('recordsFiltered' in json_response_params)

        snippets_from_json_response = json.loads(json_response.content)['data']
        self.assertEqual(len(snippets), len(snippets_from_json_response))
        self.assertEqual(snippets[0].to_dict_json(), snippets_from_json_response[0])


class SnippetJsonUserIsAuthorViewTest(TestCase):
    def setUp(self) -> None:
        self.user_1 = User.objects.create_user(username='TestUser', password='Pa55w.rd')
        self.user_2 = User.objects.create_user(username='TestUser2', password='Pa55w.rd')
        self.lang = SupportedLang.objects.create(lang='TestLang')
        self.snippet_1 = Snippet.objects.create(
            name='TestName 1',
            lang=self.lang,
            code='TestCode 1',
            is_private=False,
            author=self.user_1
        )
        self.snippet_2 = Snippet.objects.create(
            name='TestName 2',
            lang=self.lang,
            code='TestCode 2',
            is_private=False,
            author=self.user_2
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get('/ajax/snippet_user_is_author/json')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('snippet_user_is_author_json'))
        self.assertEqual(response.status_code, 200)

    def test_json_response(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippets = Snippet.objects.filter(author=self.user_1)
        json_response = self.client.get(reverse('snippet_user_is_author_json'))

        json_response_params = json.loads(json_response.content).keys()
        self.assertTrue('data' in json_response_params)
        self.assertTrue('recordsTotal' in json_response_params)
        self.assertTrue('recordsFiltered' in json_response_params)

        snippets_from_json_response = json.loads(json_response.content)['data']
        self.assertEqual(len(snippets), len(snippets_from_json_response))
        self.assertEqual(snippets[0].to_dict_json(), snippets_from_json_response[0])


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
        response = self.client.post(reverse('create_comment'), {'snippet': self.snippet.id, 'text': 'TestText'}, follow=True)
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


class SwitchSnippetlikeViewTest(TestCase):
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
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(f'/ajax/switch_snippetlike/{self.snippet.id}')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('switch_snippetlike', kwargs={'snippet_id': self.snippet.id}))
        self.assertEqual(response.status_code, 200)

    def test_view_create_and_delete_snippetlike(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        self.client.get(reverse('switch_snippetlike', kwargs={'snippet_id': self.snippet.id}))
        self.assertTrue(SnippetLike.objects.filter(snippet=self.snippet, author=self.user).exists())

        self.client.get(reverse('switch_snippetlike', kwargs={'snippet_id': self.snippet.id}))
        self.assertFalse(SnippetLike.objects.filter(snippet=self.snippet, author=self.user).exists())

